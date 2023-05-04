# Query Theme Discovery

This repository contains code for an unsupervised approach to clustering user queries for the purpose of discovering prevalent themes from the data.

## Usage

The provided Makefile handles the python virtual environment and contains a target for running the clustering script with default values.

To reduplicate the run that resulted in the clusters reported here, simply invoke the makefile target from the command line:

`make clusters`

This will create a virtual python environment, install all dependencies from `requirements.txt` in that environment, and run the `clusters.py` script with the default arguments. 

Otherwise, assuming your python environment includes the packages listed in `requirements.txt`, the python script `cluster.py` can be called directly like so:

```
python cluster.py \
	    --model roberta-base \
		--dataset spider \
		--dataset_column query \
		-k 20 \
		-r 10
```

Where: 

```
--model : the huggingface pretrained model you want to use to embed the input

--dataset : The huggingface dataset you want to embed

--dataset_column : The column of the dataset you wish to embed

-k : The number of clusters for the K-means clustering algorithm

-r : some random integer to fix the initialization state of the K-means centroids
```

The output of `clusters.py` is a series of text files, 1 per cluster, containing all the strings belonging to the associated cluster. 

After running the clustering script, you have unlabeled clusters located in the `output/clusters/` folder. To label the clusters, call the makefile target `make cluster-labels`, which feeds the clusters to an LLM to produce a cluster summary, retrieve counts, and print a markdown-formatted table of the results (see the Results section below).

## The Task

The task is to analyze a dataset of user queries and come up with 10-20 clusters of common intent, and their frequencies.

The context of the task is that we want to provide a recommendation to stakeholders on what people are asking for, to help guide future product decisions. 

## The Approach
Given the 4-hour timebox, this approach represents a first pass at where I would start in service of the described task.

### Text Representation
First, it was necessary to decide how I wanted to represent the user query data to facilitate computational processing. I chose to use a transformer-based language model encoder from the BERT family of models to embed each user query in a semantic space. Specifically, I used the `roberta-base` model from huggingface.  

Pros:
- Pretrained models are able to produce reasonable representations at the token and full text input level without additional training data.
- Pretrained models can be easily fine-tuned on different tasks, resulting in representations optimized for the given task. The representation being passed to the task-specific classification layer can be extracted and used for other tasks.
- The roBERTa model is generally accepted to be an improvement on the BERT model, trained on more data, with better hyperparameter optimization, and better performance on many of the standard panel of downstream tasks. 

Cons:
- By using the roBERTa model as an encoder without fine-tuning, I can only expect that the [CLS] token representation (the vector representing the input text as a whole, being passed to the classifier head) captures what general meaning of the input lies downstream of the token-distributional view of semantics. In many cases this is good enough, and therefore is not an unreasonable starting place. 

### Clustering
Once we have encoded our input texts into the semantic space, we can derive clusters from the data by leveraging mathematical notions of distance between points in an N-dimensional space. 

I chose the K-means clustering algorithm as a sensible baseline, since the task definition supplied an approximate K. 

Pros:
- Simple, fast, and effective.
- Being given a K value a priori circumvents the otherwise tricky problem of choosing a K to fit unfamiliar data. Choosing the upper-bound of our provided K range allows us to cluster with a mind towards merging as needed, as far as our lower-bound K. The rationale here is that merging clusters is an easier post-hoc task than dividing clusters.
- Clustering based on the full representation, not some lower dimensional projection.

Cons: 
- Possibly sensitive to the initial centroid configuration, which is controlled in sklearn by a random Int. 

With the vector representations of the user queries merged into clusters, we can examine each and assign a cluster label to characterize what we see.

### Labelling Clusters

Originally I imagined I would simply cluster and assign labels after a post-hoc perusal of the data. After all, its only 20 clusters!

Well I got lazy, and decided to invest in a script that reads in the cluster txt files and feeds them to the openai API for GPT4 to label for me. This work is contained in the `label_clusters.py` and `llm/connect_openai.py`.

The Makefile target to run this is `make cluster-labels`

## Results

The raw results of the clustering script can be found in the `output/clusters/` folder, where a text file exists for each cluster and follows the naming convention:

```cluster{cluster_number}_d={dataset}_c={dataset_column}_r={random_initialization_integer}.txt```

The cluster labeling script writes a `_description.txt` file with the descriptive label for each cluster in the `output/descriptions/` folder.

In summary, there are the results:

| Cluster | Label | Size | Example |
| ------- | ----- | ---- | ------ |
| cluster0 | Analyzing various queries related to names, demographics, statistics, and details about different subjects like athletes, pilots, races, airports, employees, and more. | 425 | What is the name of the district with the most residents?
 |
| cluster1 | Analyze various academic and student data including course enrollment, faculty information, student demographics, academic performance, and activity participation. | 365 | Find the name of the campuses opened before 1800.
 |
| cluster10 | Find compatible browser and accelerator names, medicine interactions, employee and customer details, booking information, festival nominations, languages, artwork types, student and performance data, phones, papers, documents, companies, song and movie details, product information, orders, amenities, clubs, demographic data, transaction records, policies, and document access counts. | 315 | List the names of the browser that are compatible with both 'CACHEbox' and 'Fasterfox'.
 |
| cluster11 | Analyze and summarize various data points including demographics, locations, statistics, and specific queries related to various industries, education, sports, and entertainment. | 806 | Which year had the greatest number of courses?
 |
| cluster12 | Explore various aspects of artists, songs, movies, ratings, musicals, directors, genres, and reviewers in the entertainment industry. | 242 | What are the names of the artists who released a song that has the word love in its title, and where are the artists from?
 |
| cluster13 | Generate insights regarding customer activities, employee information, transaction details, insurance policies, account balances, orders, and various business aspects across different industries. | 357 | Return the name and number of reservations made for each of the rooms.
 |
| cluster14 | Analyze various data including demographics, finances, locations, fields, and statistics related to countries, cities, industries, schools, elections, and individuals. | 227 | Return the countries of the mountains that have a height larger than 5000.
 |
| cluster15 | Analyze and provide details on various aspects of projects, roles, users, documents, services, assets, transactions, policies, and reviews in diverse data sets. | 248 | List the project details of the projects which did not hire any staff for a researcher role.
 |
| cluster16 | Analyze product information, order details, customer data, and company statistics across various industries and devices, including product prices, characteristics, ratings, events, and manufacturers. | 228 | Find the order detail for the products with price above 2000.
 |
| cluster17 | Retrieve information and statistics about various entities, such as appointments, employees, courses, products, students, customers, documents, clubs, addresses, phone numbers, locations, and more. | 437 | Find the id of the appointment with the most recent start date?
 |
| cluster18 | Summarize various sports-related queries involving wrestler statistics, athletes' information, match details, team records, college and school data, game player information, and roller coaster information. | 245 | Return the names of wrestlers with fewer than 100 days held.
 |
| cluster19 | Retrieve information about staff, institutions, medications, employees, customers, authors, problems, documents, workshops, names, companies, investors and more, including queries related to roles, departments, dates, locations, titles, nurses, and various other attributes. | 250 | Give me a list of descriptions of the problems that are reported by the staff whose first name is Christop.
 |
| cluster2 | Obtain information about students, faculty, courses, departments, University-related statistics, and other academic details. | 436 | What are the first names of all students in course ACCT-211?
 |
| cluster3 | Explore various information on singers, artists, music festivals, films, albums, songs, wines, exhibitions, books, film studios, musicals, directors, publishers, and tourist attractions. | 235 | List the name and country of origin for all singers who have produced songs with rating above 9.
 |
| cluster4 | Analyze and summarize various quantitative data and information about departments, calendars, courses, races, artists, entrepreneurs, customers, companies, projects, stadiums, users, services, labs, institutions, clubs, and locations. | 203 | Give the name of the department with the lowest budget.
 |
| cluster5 | Analyze various data related to competitions, students, sports players, investors, cities, countries, colleges, weather conditions, industries, wines, demographic information, tourist attractions, business operations, and geographic locations. | 479 | What are the types of competition and number of competitions for that type?
 |
| cluster6 | Analyze various data related to locations, amenities, routes, capacities, and other details of hotels, rooms, apartments, events, and transportation methods. | 339 | Find the most popular room in the hotel. The most popular room is the room that had seen the largest number of reservations.
 |
| cluster7 | Analyze and summarize customer, employee, product, and transaction data, including identifying top performers, calculating averages, examining purchase patterns, and evaluating financial metrics. | 417 | what are the order id and customer id of the oldest order?
 |
| cluster8 | Generate a comprehensive summary of various user queries related to location-based information, demographics, rankings, events, organizations, and specific details for various elements. | 311 | Return all the apartment numbers sorted by the room count in ascending order.
 |
| cluster9 | Obtain information on various entities, such as vehicles, products, services, documents, technicians, and customers, including their characteristics, transactions, identifiers, performances, and details across different domains like music, films, technology, education, and healthcare. | 397 | What are the ids of all vehicles?
 |

## Ideas for Improvement
Overall I believe this setup represents a respectable baseline, but there are a few areas that I think could be improved on:

### Fine-tuning to optimize query representation
The dataset we are given includes SQL queries corresponding to each of the natural language queries. If we fine-tune our encoder model on the seq2seq task of predicting the SQL translation given the English query, the representations we extract for clustering will be optimized representations of the text which predict the explicit, functional intent of the query. My intuition around text representation makes me think this could be better-suited for our task, which is to discover the types of intents people are trying to convey through their prose, and avoids us having to wade through possible noise of a natural language interface. 

Of course, this intuition would need to be borne out empirically, but a cursory glance at the clustered output reveals many examples which appear to be together on the basis of lexical overlap more than query intent.

### Evaluation of cluster quality
The scope of this project meant that my evaluation of cluster quality was restricted to browsing the clusters manually to make sure that the results were reasonable. Given a bit more time, it would be useful to implement some intrinsic and extrinsic measures of cluster quality. For example:

- <b>Intrinsic evaluation</b>: we could calculate the cluster cardinality (# of examples per cluster) and cluster magnitude (sum of distances of each point in a cluster from its centroid). We could observe anomalies in these two metrics individually, and also plot the magnitude over cardinality and spot clusters whose correlation is anomalous relative to the other clusters. 
- <b>Extrinsic Evaluation</b>: assuming the clusters are consumed as features for some downstream model or system, we could measure the performance delta between different runs of the clustering model to determine which configuration has the optimal intended effect.