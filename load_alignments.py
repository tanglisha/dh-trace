import json

from tqdm import tqdm

from database_ops import (insert_alignments_to_db, insert_last_run_stats_to_db,
                          read_all_author_names_and_ids_from_db,
                          read_all_text_names_and_ids_from_db,
                          read_all_text_names_by_id_from_db,
                          read_all_text_pair_names_and_ids_from_db,
                          read_author_names_by_id_from_db)
from util import (fix_the_gd_author_name_from_aligns, get_project_name,
                  getCountOfFiles)

author_and_id_dict = read_all_author_names_and_ids_from_db()
inverted_authors = read_author_names_by_id_from_db()
text_and_id_dict = read_all_text_names_and_ids_from_db()
inverted_text_and_id_dict = read_all_text_names_by_id_from_db()
project_name = get_project_name()
total_file_count = getCountOfFiles(f'./projects/{project_name}/splits')
text_pairs, inverted_pairs = read_all_text_pair_names_and_ids_from_db()
transactions = []

#Alignments
i = 1
with open(f'./projects/{project_name}/alignments/alignments.jsonl', 'r') as the_json:
    raw_json_list = list(the_json)
    length_json_list = len(raw_json_list)
    total_entries_in_alignments_file = length_json_list
    while i <= length_json_list:
        pbar = tqdm(desc='Loading Alignments', total=length_json_list, colour="magenta", bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} | Elapsed: [{elapsed}]')
        for json_str in raw_json_list:
            result = json.loads(json_str)
            temp_source_author = fix_the_gd_author_name_from_aligns(result['source_author'])
            source_author = author_and_id_dict[temp_source_author]
            source_text_name = text_and_id_dict[result['source_filename'].split('TEXT/')[1]]
            temp_target_author = fix_the_gd_author_name_from_aligns(result['target_author'])
            target_author = author_and_id_dict[temp_target_author]
            target_text_name = text_and_id_dict[result['target_filename'].split('TEXT/')[1]]
            try:
                pair_id = inverted_pairs[(source_text_name, target_text_name)]
            except KeyError:
                pair_id = inverted_pairs[(target_text_name, source_text_name)]
            #The split below is part of the text-pair output path.
            transactions.append((source_text_name, target_text_name, result['source_passage'], result['target_passage'], source_author, target_author, len(result['source_passage'].split(' ')), len(result['target_passage'].split(' ')), pair_id))
            i+=1
            pbar.update(1)
        pbar.close()

insert_alignments_to_db(transactions)
insert_last_run_stats_to_db(total_entries_in_alignments_file, total_file_count)