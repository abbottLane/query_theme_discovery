from llm.connect_openai import chatgpt_response
import logging
import os
import argparse
import random
import asyncio

OUTPUT_FOLDER = "./output/"

async def main():
    """
    Assuming a folder of text files containing clusters of lines, this function will label each cluster with a one-line description using chatgpt
    and print a markdown-formatted table of the summary stats
    """
    cluster_data = {}
    # for each file in the the ./output folder, read all the lines
    cluster_folder = OUTPUT_FOLDER + "clusters/"
    for filename in os.listdir(cluster_folder):
        if filename.startswith("cluster"): # we need to stick with the naming convention because descriptions are also stored in this folder
            cluster = filename.split("_")[0]
            with open(cluster_folder + filename, 'r') as f:
                lines = f.readlines()
                lines_str = sample_lines(lines, token_count=3000)
        
            # for each line, send it to chatgpt
            try:
                response = await chatgpt_response(lines_str)
                if "there are no" in response:
                    response = "No description available"
                cluster_data[cluster] = {"label": response, "data": lines}
            except Exception as e:
                logging.info('CHATGPT Error: ', e)

            with open(OUTPUT_FOLDER + "descriptions/" + cluster + "_description.txt", 'w') as f:
                f.write(response)
            
            # sleep for 10 second to avoid rate limiting. Yes i know :'[
            await asyncio.sleep(10)
        
    # print cluster stats table
    print(get_stats(cluster_data))

def sample_lines(lines, token_count=3000):
    """
    This function takes a list of lines and returns a string of randomly sampled lines that is less than the token count, where tokens are whitespace delineated
    returns: string
    """
    random.shuffle(lines)
    lines_str = ""
    for line in lines:
        if len(lines_str.split()) < token_count:
            lines_str += line
        else:
            break
    return lines_str

def get_stats(cluster_data):
    """
    This function takes the labelled clusters and corresponding lines and returns a markdown-formatted table of the stats
    returns: string
    """
    stats = "| Cluster | Label | Size | Example |\n"
    stats += "| ------- | ----- | ---- | ------ |\n"
    for cluster in sorted(cluster_data.keys()):
        stats += "| " + cluster + " | " + cluster_data[cluster]["label"] + " | " + str(len(cluster_data[cluster]["data"])) + " | " + cluster_data[cluster]["data"][0].rstrip() + " |\n"
    return stats
    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input_dir", type=str, default=OUTPUT_FOLDER, help="The directory where the strings for each cluster are stored")
    args = argparser.parse_args()

    OUTPUT_FOLDER = args.input_dir

    asyncio.run(main())