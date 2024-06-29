import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
import sys

def read_csv(name):
    """
    Reads a CSV file and returns a dataframe with the specified headers.
    """
    headers = ['SegmentNr', 'Position', 'A', 'C', 'G', 'T']
    df = pd.read_csv(name, names=headers)
    return df

def clean_data(df):
    """
    Cleans the dataframe by handling missing positions, duplicated positions, wrong positions,
    and duplicated segments.
    """
    required_columns = ['SegmentNr', 'Position', 'A', 'C', 'G', 'T']
    
    # Check if required columns are present
    for column in required_columns:
        if column not in df.columns:
            raise KeyError(f"Missing required column: {column}")
    
    cleaned_df = pd.DataFrame()
    for segment, group in df.groupby('SegmentNr'):
        max_position = group['Position'].max()
        positions = set(group['Position'])

        # Check for missing positions
        if len(positions) != max_position:
            continue

        # Check for duplicated positions
        if group.duplicated(subset=['Position']).any():
            if not group.duplicated(subset=['Position', 'A', 'C', 'G', 'T']).all():
                continue
            group = group.drop_duplicates(subset=['Position', 'A', 'C', 'G', 'T'])

        # Check for wrong positions
        if ((group[['A', 'C', 'G', 'T']].sum(axis=1) != 1).any() or
            (group[['A', 'C', 'G', 'T']] > 1).any().any()):
            continue

        cleaned_df = pd.concat([cleaned_df, group])

    # Check for duplicated segments
    sequences = cleaned_df.groupby('SegmentNr').apply(lambda x: ''.join(x[['A', 'C', 'G', 'T']].idxmax(axis=1)), include_groups=False)
    duplicates = sequences[sequences.duplicated()]
    cleaned_df = cleaned_df[~cleaned_df['SegmentNr'].isin(duplicates.index)]

    return cleaned_df

def generate_sequences(df):
    """
    Generates JSON sequences from the dataframe.
    """
    sequences = df.groupby('SegmentNr').apply(lambda x: ''.join(x[['A', 'C', 'G', 'T']].idxmax(axis=1)), include_groups=False)
    sequences_json = sequences.to_json()
    return json.loads(sequences_json)

def construct_graph(json_data, k):
    """
    Constructs the de Bruijn graph from the JSON data.
    """
    G = nx.MultiDiGraph()
    for segment, sequence in json_data.items():
        for i in range(len(sequence) - k + 1):
            kmer = sequence[i:i+k]
            L, R = kmer[:-1], kmer[1:]
            if not G.has_node(L):
                G.add_node(L)
            if not G.has_node(R):
                G.add_node(R)
            G.add_edge(L, R)
    return G

def plot_graph(graph, filename):
    """
    Plots the de Bruijn graph and saves it as a PNG file.
    """
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=5000, node_color='skyblue', font_size=10, font_weight='bold')
    plt.savefig(filename)

def is_valid_graph(graph):
    """
    Checks whether the de Bruijn graph satisfies the conditions of having an Euler's path.
    """
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    start_nodes = 0
    end_nodes = 0
    for node in graph.nodes:
        if in_degrees[node] == out_degrees[node]:
            continue
        elif in_degrees[node] == out_degrees[node] + 1:
            end_nodes += 1
        elif out_degrees[node] == in_degrees[node] + 1:
            start_nodes += 1
        else:
            return False
    return (start_nodes == 1 and end_nodes == 1) or (start_nodes == 0 and end_nodes == 0)

def construct_dna_sequence(graph):
    """
    Constructs the DNA sequence from the de Bruijn graph.
    """
    if not is_valid_graph(graph):
        return "DNA sequence cannot be constructed."
    
    eulerian_path = list(nx.eulerian_path(graph))
    dna_sequence = eulerian_path[0][0]
    for edge in eulerian_path:
        dna_sequence += edge[1][-1]
    return dna_sequence

def save_output(s, filename):
    """
    Saves the DNA sequence or error message to a file.
    """
    with open(filename, 'w') as file:
        file.write(s)

def main():
    if len(sys.argv) != 2:
        print("Usage: python project.py DNA[x][k].csv")
        return
    
    input_file = sys.argv[1]
    x = input_file.split('_')[1]
    k = int(input_file.split('_')[2].split('.')[0])
    
    df = read_csv(input_file)
    cleaned_df = clean_data(df)
    sequences_json = generate_sequences(cleaned_df)
    graph = construct_graph(sequences_json, k)
    plot_filename = f'DNA_{x}.png'
    plot_graph(graph, plot_filename)
    
    if is_valid_graph(graph):
        dna_sequence = construct_dna_sequence(graph)
        output = dna_sequence
    else:
        output = "DNA sequence cannot be constructed."
    
    output_filename = f'DNA_{x}.txt'
    save_output(output, output_filename)
    print(f"Graph plot saved to {plot_filename}")
    print(f"Output saved to {output_filename}")

if __name__ == "__main__":
    main()
