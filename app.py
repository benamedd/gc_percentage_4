# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import math
import re
import io
import base64

# -----------------------
# Configuration page & PWA
# -----------------------
st.set_page_config(
    page_title="DNA Sequence Statistics Calculator",
    page_icon="icon-192.png",  # icône locale à placer à la racine du repo
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/benamedd/gc_percentage_4',
        'Report a bug': "https://github.com/benamedd/gc_percentage_4/issues",
        'About': "# DNA Sequence Calculator PWA\nAnalyze DNA sequences on any device!"
    }
)

def inject_pwa_code():
    # Injecte manifest + enregistrement service worker + bouton d'installation
    pwa_code = """
    <script>
    // Enregistrement du Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
          .then(reg => console.log('ServiceWorker registered:', reg.scope))
          .catch(err => console.log('ServiceWorker failed:', err));
      });
    }

    // beforeinstallprompt pour custom install button
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      const btn = document.createElement('button');
      btn.textContent = '?? Installer l\\'application';
      btn.style.cssText = `
        position: fixed; top: 10px; right: 10px; z-index: 1000;
        background: #4CAF50; color: white; border: none;
        padding: 10px 15px; border-radius: 6px; cursor: pointer;
      `;
      btn.addEventListener('click', () => {
        btn.style.display = 'none';
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(() => deferredPrompt = null);
      });
      document.body.appendChild(btn);
    });
    </script>

   <link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#4CAF50">

    """
    st.components.v1.html(pwa_code, height=0)

inject_pwa_code()

# -----------------------
# Helper functions for sequence stats
# -----------------------
def clean_sequence(text):
    """
    Accept FASTA or raw sequence, return uppercase sequence with only A,T,G,C,N.
    """
    if not text:
        return ""
    text = text.strip()
    # Remove FASTA header if present
    if text.startswith(">"):
        lines = text.splitlines()
        lines = [ln for ln in lines if not ln.startswith(">")]
        seq = "".join(lines)
    else:
        seq = text.replace("\n", "").replace(" ", "")
    seq = seq.upper()
    # Keep only ATGCN
    seq = re.sub(r'[^ATGCN]', '', seq)
    return seq

def base_counts(seq):
    c = Counter(seq)
    A = c.get('A', 0)
    T = c.get('T', 0)
    G = c.get('G', 0)
    C = c.get('C', 0)
    N = c.get('N', 0)
    total = A+T+G+C+N
    return {'A':A,'T':T,'G':G,'C':C,'N':N,'total': total}

def gc_content(seq):
    counts = base_counts(seq)
    total_bases = counts['A'] + counts['T'] + counts['G'] + counts['C']
    if total_bases == 0:
        return 0.0
    gc = (counts['G'] + counts['C']) / total_bases * 100
    return gc

def at_content(seq):
    counts = base_counts(seq)
    total_bases = counts['A'] + counts['T'] + counts['G'] + counts['C']
    if total_bases == 0:
        return 0.0
    at = (counts['A'] + counts['T']) / total_bases * 100
    return at

def gc_skew(seq, window=100):
    """
    Return list of (pos_center, skew) where skew = (G - C) / (G + C) in sliding window.
    If G + C == 0 => skew = 0
    """
    seq = seq.upper()
    n = len(seq)
    positions = []
    skews = []
    if n == 0:
        return positions, skews
    half = window // 2
    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half + 1)
        w = seq[start:end]
        g = w.count('G')
        c = w.count('C')
        denom = g + c
        skew = (g - c) / denom if denom != 0 else 0.0
        positions.append(i + 1)  # 1-based
        skews.append(skew)
    return positions, skews

def dinucleotide_freq(seq):
    seq = seq.upper()
    di = Counter()
    for i in range(len(seq)-1):
        d = seq[i:i+2]
        if re.fullmatch(r'[ATGC]{2}', d):
            di[d] += 1
    total = sum(di.values())
    freqs = {k: (v, v/total if total>0 else 0) for k,v in di.items()}
    return freqs, total

def cpg_oe(seq):
    seq = seq.upper()
    counts = base_counts(seq)
    total_bases = counts['A'] + counts['T'] + counts['G'] + counts['C']
    if total_bases == 0:
        return None
    cg = sum(1 for i in range(len(seq)-1) if seq[i:i+2] == 'CG')
    G = counts['G']
    C = counts['C']
    expected = (G * C) / total_bases if total_bases>0 else 0
    if expected == 0:
        return None
    oe = cg / expected
    return oe

def shannon_entropy(seq, k=1):
    # For k=1 mononucleotide entropy
    seq = seq.upper()
    n = len(seq)
    if n == 0:
        return 0.0
    counts = Counter(seq)
    # keep only ATGC
    total = sum(counts[b] for b in 'ATGC')
    if total == 0:
        return 0.0
    H = 0.0
    for b in 'ATGC':
        p = counts.get(b, 0) / total
        if p > 0:
            H -= p * math.log2(p)
    return H

def longest_run(seq, base):
    # longest consecutive run of a base
    pattern = f'({base}+)'
    runs = re.findall(pattern, seq.upper())
    if not runs:
        return 0
    return max(len(r) for r in runs)

def compute_tm(seq):
    # Simple Wallace rule: Tm = 2*(A+T) + 4*(G+C) for short sequences
    counts = base_counts(seq)
    at = counts['A'] + counts['T']
    gc = counts['G'] + counts['C']
    if at+gc == 0:
        return None
    tm = 2 * at + 4 * gc
    return tm

# -----------------------
# UI layout
# -----------------------
st.title("DNA Sequence Calculator")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Entrer la séquence (FASTA ou plain)")
    seq_input = st.text_area(
        "Séquence ADN :",
        height=220,
        placeholder="Exemple: ATGCGCTAGCTAGCTAGCATGC ou format FASTA (commençant par >header)"
    )
    btn = st.button("Analyser")

with col2:
    st.subheader("Options")
    window = st.number_input("Fenêtre pour GC-skew (bp)", min_value=10, max_value=10000, value=201, step=2)
    show_plots = st.checkbox("Afficher graphiques", value=True)
    download_report = st.checkbox("Préparer CSV pour téléchargement", value=True)

# -----------------------
# Process input when user clicks
# -----------------------
if btn:
    seq = clean_sequence(seq_input)
    if len(seq) == 0:
        st.error("Séquence vide ou format non reconnu après nettoyage. Vérifiez votre entrée.")
    else:
        counts = base_counts(seq)
        gc = gc_content(seq)
        at = at_content(seq)
        oe = cpg_oe(seq)
        entropy = shannon_entropy(seq)
        tm = compute_tm(seq)
        longest_A = longest_run(seq, 'A')
        longest_T = longest_run(seq, 'T')
        longest_G = longest_run(seq, 'G')
        longest_C = longest_run(seq, 'C')
        di_freqs, di_total = dinucleotide_freq(seq)

        # Summary metrics
        st.header("Résultats")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        metrics_col1.metric("Longueur (bp)", counts['total'])
        metrics_col1.metric("GC (%)", f"{gc:.2f}")
        metrics_col1.metric("AT (%)", f"{at:.2f}")

        metrics_col2.metric("Shannon Entropy (mono)", f"{entropy:.3f}")
        metrics_col2.metric("CpG O/E", f"{oe:.3f}" if oe is not None else "NA")
        metrics_col2.metric("Tm (approx)", f"{tm}" if tm is not None else "NA")

        metrics_col3.metric("Longest A run", longest_A)
        metrics_col3.metric("Longest T run", longest_T)
        metrics_col3.metric("Longest G run", longest_G)
        metrics_col3.metric("Longest C run", longest_C)

        # Base composition barplot
        if show_plots:
            comp_fig = px.bar(
                x=['A','T','G','C','N'],
                y=[counts['A'], counts['T'], counts['G'], counts['C'], counts['N']],
                labels={'x':'Base','y':'Count'},
                title="Composition des bases"
            )
            st.plotly_chart(comp_fig, use_container_width=True)

            # GC skew plot (sampled for large sequences)
            pos, skews = gc_skew(seq, window=int(window))
            # downsample for display if too long
            max_points = 2000
            if len(pos) > max_points:
                step = max(1, len(pos)//max_points)
                pos_ds = pos[::step]
                skews_ds = skews[::step]
            else:
                pos_ds = pos
                skews_ds = skews

            skew_fig = go.Figure()
            skew_fig.add_trace(go.Scatter(x=pos_ds, y=skews_ds, mode='lines', name='GC Skew'))
            skew_fig.update_layout(title=f'GC skew (window={window} bp)', xaxis_title='Position (bp)', yaxis_title='Skew')
            st.plotly_chart(skew_fig, use_container_width=True)

            # Dinucleotide frequencies table
            di_df = pd.DataFrame(
                [(k, v[0], v[1]) for k, v in sorted(di_freqs.items())],
                columns=['Dinucleotide','Count','Frequency']
            ).sort_values('Dinucleotide')
            st.subheader("Fréquences dinucléotidiques")
            st.dataframe(di_df)

        # Prepare CSV download
        if download_report:
            data = {
                'Metric': [
                    'Length_bp','GC_percent','AT_percent','Shannon_entropy','CpG_OE','Tm_approx',
                    'LongestA','LongestT','LongestG','LongestC'
                ],
                'Value': [
                    counts['total'], f"{gc:.4f}", f"{at:.4f}", f"{entropy:.6f}",
                    (f"{oe:.6f}" if oe is not None else "NA"),
                    (f"{tm}" if tm is not None else "NA"),
                    longest_A, longest_T, longest_G, longest_C
                ]
            }
            df_metrics = pd.DataFrame(data)

            # dinuc table appended
            if di_total > 0:
                di_table = pd.DataFrame([(k, v[0], v[1]) for k, v in sorted(di_freqs.items())],
                                        columns=['Dinucleotide','Count','Frequency'])
            else:
                di_table = pd.DataFrame(columns=['Dinucleotide','Count','Frequency'])

            # Create Excel-like CSVs concatenated or create a single zip? We'll create a single CSV with a separator section
            buf = io.StringIO()
            buf.write("# Metrics\n")
            df_metrics.to_csv(buf, index=False)
            buf.write("\n# Dinucleotide frequencies\n")
            di_table.to_csv(buf, index=False)
            csv_data = buf.getvalue().encode('utf-8')

            st.download_button(
                label="Télécharger le rapport CSV",
                data=csv_data,
                file_name="dna_stats_report.csv",
                mime="text/csv"
            )

        # show a small sample of the cleaned sequence and first 200 bp
        st.subheader("Aperçu de la séquence (nettoyée)")
        st.code(seq[:1000] + ("..." if len(seq) > 1000 else ""))

# Footer / debug
st.markdown("---")
st.markdown("Développé pour PWA — assurez-vous que `manifest.json`, `service-worker.js`, `icon-192.png` et `icon-512.png` sont à la racine du repo.")

# End of file
