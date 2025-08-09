import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import math

st.set_page_config(
    page_title="DNA Sequence Statistics Calculator",
    page_icon="🧬",
    layout="wide"
)

def clean_sequence(sequence):
    lines = sequence.strip().split('\n')
    clean_lines = [line for line in lines if not line.startswith('>')]
    clean_seq = ''.join(clean_lines).upper().replace(' ', '')
    clean_seq = re.sub(r'[^ATGCN]', '', clean_seq)
    return clean_seq

def compute_gc_skew(sequence):
    G = sequence.count('G')
    C = sequence.count('C')
    return (G - C) / max(G + C, 1)

def compute_at_skew(sequence):
    A = sequence.count('A')
    T = sequence.count('T')
    return (A - T) / max(A + T, 1)

def compute_entropy(sequence):
    # Entropie sur les bases A/T/G/C uniquement
    total = len(sequence)
    if total == 0:
        return 0.0
    freqs = {
        'A': sequence.count('A') / total,
        'T': sequence.count('T') / total,
        'G': sequence.count('G') / total,
        'C': sequence.count('C') / total
    }
    H = 0.0
    for p in freqs.values():
        if p > 0:
            H -= p * math.log(p, 2)
    return round(H, 4)

def compute_tm(sequence):
    # Formule simple de Wallace (estimation rapide)
    A = sequence.count('A')
    T = sequence.count('T')
    G = sequence.count('G')
    C = sequence.count('C')
    length = len(sequence)
    if length <= 0:
        return None
    if length <= 14:
        tm = 2 * (A + T) + 4 * (G + C)
    else:
        tm = 64.9 + 41 * ((G + C) - 16.4) / length
    return round(tm, 2)

def compute_cpg_oe(sequence):
    # CpG Observed/Expected
    c = sequence.count('C')
    g = sequence.count('G')
    cg_obs = sequence.count('CG')
    N = len(sequence)
    if N <= 1:
        return {'CG_obs': 0, 'CG_exp': 0, 'CpG_OE': 0}
    cg_exp = max((c * g) / (N - 1), 1e-9)
    oe = cg_obs / cg_exp if cg_exp > 0 else 0
    return {'CG_obs': cg_obs, 'CG_exp': cg_exp, 'CpG_OE': oe}

def compute_window_gc(sequence, window_size):
    w = int(window_size)
    if w <= 0 or len(sequence) < w:
        return []
    gc_values = []
    for i in range(len(sequence) - w + 1):
        win = sequence[i:i+w]
        gc = (win.count('G') + win.count('C')) / w * 100
        gc_values.append(gc)
    return gc_values

def compute_dinucleotide_freq(sequence):
    seq = sequence
    if len(seq) < 2:
        return {d: 0 for d in [a+b for a in 'ACGT' for b in 'ACGT']}
    dinos = [seq[i:i+2] for i in range(len(seq) - 1)]
    counts = Counter(dinos)
    all_dinucs = [a+b for a in 'ACGT' for b in 'ACGT']
    return {d: counts.get(d, 0) for d in all_dinucs}

def max_mononucleotide_run(sequence):
    if not sequence:
        return 0
    max_run = 1
    current = 1
    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i-1]:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 1
    return max_run

def calculate_stats(sequence, window_size=0):
    if not sequence:
        return None

    counter = Counter(sequence)
    total_length = len(sequence)
    A = counter.get('A', 0)
    T = counter.get('T', 0)
    G = counter.get('G', 0)
    C = counter.get('C', 0)
    N = counter.get('N', 0)

    stats = {
        'Total length': total_length,
        'A': A,
        'T': T,
        'G': G,
        'C': C,
        'N': N
    }

    if total_length > 0:
        stats['A%'] = round((A / total_length) * 100, 2)
        stats['T%'] = round((T / total_length) * 100, 2)
        stats['G%'] = round((G / total_length) * 100, 2)
        stats['C%'] = round((C / total_length) * 100, 2)
        stats['N%'] = round((N / total_length) * 100, 2)
        stats['GC%'] = round(((G + C) / total_length) * 100, 2)
        stats['AT%'] = round(((A + T) / total_length) * 100, 2)

    # Metrics additionnels
    stats['GC_Skew'] = round(compute_gc_skew(sequence), 4)
    stats['AT_Skew'] = round(compute_at_skew(sequence), 4)
    stats['Entropy'] = compute_entropy(sequence)
    stats['Tm (°C)'] = compute_tm(sequence)

    cpg = compute_cpg_oe(sequence)
    stats['CpG_obs'] = cpg['CG_obs']
    stats['CpG_exp'] = cpg['CG_exp']
    stats['CpG_OE'] = round(cpg['CpG_OE'], 4)

    stats['Longest_mononucleotide_run'] = max_mononucleotide_run(sequence)

    # Window GC content
    if window_size and window_size > 0:
        wgc = compute_window_gc(sequence, window_size)
        if wgc:
            stats['Window_GC_Avg'] = round(sum(wgc) / len(wgc), 2)
            stats['Window_GC_Min'] = round(min(wgc), 2)
            stats['Window_GC_Max'] = round(max(wgc), 2)
        else:
            stats['Window_GC_Avg'] = None
            stats['Window_GC_Min'] = None
            stats['Window_GC_Max'] = None
        stats['Window_GC_Series'] = wgc
    else:
        stats['Window_GC_Avg'] = None
        stats['Window_GC_Min'] = None
        stats['Window_GC_Max'] = None
        stats['Window_GC_Series'] = []

    # Dinucleotide frequencies
    stats['Dinucleotide_table'] = compute_dinucleotide_freq(sequence)

    return stats

def create_composition_chart(stats):
    if not stats:
        return None
    nucleotides = ['A', 'T', 'G', 'C']
    counts = [stats[nuc] for nuc in nucleotides]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    fig = go.Figure(data=[go.Pie(
        labels=nucleotides,
        values=counts,
        hole=0.3,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
    )])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title="Nucleotide Composition",
        font=dict(size=14),
        showlegend=True,
        height=400
    )
    return fig

def create_bar_chart(stats):
    if not stats:
        return None
    nucleotides = ['A%', 'T%', 'G%', 'C%']
    percentages = [stats[nuc] for nuc in nucleotides]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    fig = go.Figure(data=[go.Bar(
        x=[nuc.replace('%', '') for nuc in nucleotides],
        y=percentages,
        marker=dict(color=colors),
        text=[f"{p}%" for p in percentages],
        textposition='auto'
    )])
    fig.update_layout(
        title="Nucleotide Percentages",
        xaxis_title="Nucleotides",
        yaxis_title="Percentage (%)",
        height=400,
        yaxis=dict(range=[0, max(percentages) + 5])
    )
    return fig

@st.cache_data(show_spinner=False)
def flatten_stats_for_csv(stats: dict) -> pd.DataFrame:
    # Aplatir les stats pour export CSV
    flat = {k: v for k, v in stats.items() if k not in ['Dinucleotide_table', 'Window_GC_Series']}
    for di, count in stats.get('Dinucleotide_table', {}).items():
        flat[f'Di_{di}'] = count
    return pd.DataFrame([flat])

@st.cache_data(show_spinner=False)
def window_gc_df(seq: str, w: int) -> pd.DataFrame:
    values = compute_window_gc(seq, w)
    if not values:
        return pd.DataFrame(columns=['start', 'end', 'GC_percent'])
    starts = list(range(0, len(seq) - w + 1))
    df = pd.DataFrame({
        'start': [s + 1 for s in starts],            # 1-based indexing
        'end':   [s + w for s in starts],
        'GC_percent': values
    })
    return df

def dinuc_heatmap_df(dinuc_dict: dict) -> pd.DataFrame:
    bases = list('ACGT')
    data = []
    for a in bases:
        row = []
        for b in bases:
            row.append(dinuc_dict.get(a+b, 0))
        data.append(row)
    return pd.DataFrame(data, index=bases, columns=bases)

# UI
st.title("🧬 DNA Sequence Statistics Calculator")
st.markdown("---")
st.markdown("""
### How to use
1. Paste your sequence in the text area below
2. The sequence can be in FASTA format
3. Analysis is performed automatically
4. You can download results as CSV
""")

sequence_input = st.text_area(
    "Paste your DNA sequence here:",
    height=200,
    placeholder="Example: ATGCGCTAGCTAGCTAGCATGC"
)

if sequence_input:
    clean_seq = clean_sequence(sequence_input)

    if not clean_seq:
        st.warning("La séquence fournie ne contient aucun caractère valide (A/T/G/C/N).")
        st.stop()

    max_window = max(1, len(clean_seq))
    default_w = 1000 if max_window >= 1000 else max_window
    window_size = st.number_input(
        "Taille de la fenêtre glissante pour le GC (%) (0 pour désactiver)",
        min_value=0,
        max_value=max_window,
        value=default_w,
        step=min(50, max_window)
    )

    # Calcul des stats
    stats = calculate_stats(clean_seq, window_size if window_size > 0 else 0)

    # Metrics principaux
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total length", f"{stats['Total length']}")
    col1.metric("GC%", f"{stats['GC%']}%")
    col1.metric("AT%", f"{stats['AT%']}%")

    col2.metric("A%", f"{stats['A%']}%")
    col2.metric("T%", f"{stats['T%']}%")
    col2.metric("N%", f"{stats['N%']}%")

    col3.metric("G%", f"{stats['G%']}%")
    col3.metric("C%", f"{stats['C%']}%")
    col3.metric("Longest mono-nuc run", f"{stats['Longest_mononucleotide_run']}")

    col4.metric("GC Skew", f"{stats['GC_Skew']}")
    col4.metric("AT Skew", f"{stats['AT_Skew']}")
    tm_display = "-" if stats['Tm (°C)'] is None else f"{stats['Tm (°C)']} °C"
    col4.metric("Tm (est.)", tm_display)

    with st.expander("Plus de métriques"):
        c1, c2, c3 = st.columns(3)
        c1.write(f"Entropy (Shannon): {stats['Entropy']}")
        c2.write(f"CpG observed: {stats['CpG_obs']}")
        c3.write(f"CpG expected: {round(stats['CpG_exp'], 2)}")
        c1.write(f"CpG O/E: {stats['CpG_OE']}")
        if window_size and window_size > 0:
            c2.write(f"Window GC avg: {stats['Window_GC_Avg'] if stats['Window_GC_Avg'] is not None else '-'}")
            c3.write(f"Window GC min/max: {stats['Window_GC_Min']} / {stats['Window_GC_Max']}")

    # Graphiques composition
    c_left, c_right = st.columns(2)
    with c_left:
        pie_fig = create_composition_chart(stats)
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True)
    with c_right:
        bar_fig = create_bar_chart(stats)
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)

    # GC par fenêtre
    if window_size and window_size > 0:
        if len(clean_seq) < window_size:
            st.info("La séquence est plus courte que la fenêtre — métrique GC par fenêtre désactivée.")
        else:
            st.markdown("#### GC% par fenêtre (sliding window)")
            wgc_df = window_gc_df(clean_seq, int(window_size))
            if not wgc_df.empty:
                line_fig = go.Figure()
                line_fig.add_trace(go.Scatter(
                    x=wgc_df['start'],
                    y=wgc_df['GC_percent'],
                    mode='lines',
                    line=dict(color='#45B7D1'),
                    name='GC% (window)'
                ))
                line_fig.update_layout(
                    xaxis_title="Start position (1-based)",
                    yaxis_title="GC (%)",
                    height=350,
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(line_fig, use_container_width=True)
                with st.expander("Télécharger le GC par fenêtre (CSV)"):
                    st.dataframe(wgc_df, use_container_width=True, height=250)
                    st.download_button(
                        "Télécharger CSV (GC par fenêtre)",
                        data=wgc_df.to_csv(index=False).encode('utf-8'),
                        file_name="window_gc.csv",
                        mime="text/csv"
                    )

    # Fréquences dinucléotidiques
    st.markdown("#### Fréquences dinucléotidiques")
    dinuc_dict = stats.get('Dinucleotide_table', {})
    if dinuc_dict:
        heat_df = dinuc_heatmap_df(dinuc_dict)
        heat_fig = px.imshow(
            heat_df,
            labels=dict(x="Second base", y="First base", color="Count"),
            x=list(heat_df.columns),
            y=list(heat_df.index),
            color_continuous_scale="Blues",
            aspect="auto"
        )
        heat_fig.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(heat_fig, use_container_width=True)
        with st.expander("Tableau dinucléotides + téléchargement"):
            # Tableau à plat
            dinuc_flat_df = pd.DataFrame(
                [{'Dinucleotide': k, 'Count': v} for k, v in dinuc_dict.items()]
            ).sort_values('Dinucleotide')
            st.dataframe(dinuc_flat_df, use_container_width=True, height=260)
            st.download_button(
                "Télécharger CSV (dinucléotides)",
                data=dinuc_flat_df.to_csv(index=False).encode('utf-8'),
                file_name="dinucleotide_frequencies.csv",
                mime="text/csv"
            )

    # Téléchargement des stats globales
    st.markdown("#### Télécharger les statistiques")
    stats_df = flatten_stats_for_csv(stats)
    st.dataframe(stats_df, use_container_width=True, height=280)
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "Télécharger CSV (statistiques globales)",
            data=stats_df.to_csv(index=False).encode('utf-8'),
            file_name="sequence_stats.csv",
            mime="text/csv"
        )
    with col_dl2:
        # Inclure la séquence nettoyée dans un fichier texte
        st.download_button(
            "Télécharger la séquence nettoyée (FASTA-like)",
            data=f">sequence_cleaned\n{clean_seq}\n".encode('utf-8'),
            file_name="sequence_cleaned.fasta",
            mime="text/plain"
        )

else:
    st.info("Collez votre séquence DNA (A/T/G/C/N) ou un FASTA pour commencer l'analyse.")
