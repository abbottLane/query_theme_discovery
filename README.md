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

In summary, these are the results:

| Cluster | Label | Size | Example |
| ------- | ----- | ---- | ------ |
| cluster0 | Gather information on various queries related to flight, ship, and race details, player and staff information, and various statistics from different categories such as geography, sports, and organizations. | 425 | What is the name of the aircraft that was on flight number 99? |
| cluster1 | Analyze various aspects of students, faculty, courses, and institutions, including demographics, affiliations, course offerings, performance, and advisor relationships. | 365 | Find the first name and office of history professor who did not get a Ph.D. degree. |
| cluster10 | Retrieve information about students' login names, course enrollments, various product and course details, club memberships, user names and emails, apartments details and addresses, document and policy information, along with item lists, transaction data, and sports team information. | 315 | Return the login names of the students whose family name is "Ward". |
| cluster11 | Statistics and information about various domains such as education, business, entertainment, sports, and more. | 806 | How many teachers does the student named MADLOCK RAY have? |
| cluster12 | Explore various aspects of movies, music, artists, albums, directors, reviewers, ratings, languages, and genres in the entertainment industry. | 242 | What are the dates of ceremony at music festivals corresponding to volumes that lasted more than 2 weeks on top? |
| cluster13 | Analyze and summarize financial data, customer information, employee details, transaction records, invoice and order statuses, claims and settlements, account balances, and various other attributes to provide insights on customer behavior, employee performance, and overall business performance. | 357 | Show the average share count of transactions for different investors. |
| cluster14 | Analyze various data regarding mountains, employees, airports, students, schools, companies, tracks, apartments, competitions, departments, sports, populations, cities, election cycles, engineers, artists, committees, delegates, entrepreneurs, transit passengers, aircrafts, markets, journalists, crime rates, temperatures, recordholders, cameras, financiers, films, actors, and organized events, utilizing minimum, maximum, average, and other computed values. | 227 | Show the countries that have mountains with height more than 5600 stories and mountains with height less than 5200. |
| cluster15 | Generate summaries and statistics of various data entities including documents, projects, users, services, policies, roles, transactions, and attributes. | 248 | List all the image name and URLs in the order of their names. |
| cluster16 | Analyze product information, customer data, supplier details, manufacturer revenue, product prices, characteristics, and order quantities to provide insights on various aspects like top customers, most expensive item, shop stocks, average prices, carrier usage, company sales, industry market values, product ratings, and more. | 228 | Return ids of all the products that are supplied by supplier id 2 and are more expensive than the average price of all products. |
| cluster17 | Consolidated description: Retrieve various information about clubs, songs, products, addresses, artists, documents, phones, courses, enzymes, employees, customer details, and other entities from a diverse set of data. | 437 | Which clubs have one or more members whose advisor is "1121"? |
| cluster18 | Analyze and provide various statistics, lists, and information about players, games, teams, clubs, and other related aspects in sports, associations, and competitions. | 245 | List the ids of all distinct orders ordered by placed date. |
| cluster19 | Retrieve information on customers, employees, institutions, authors, physicians, students, club members, papers, reports, activities, and various details such as names, roles, dates, titles, and phone numbers. | 250 | What are the names of customers who never made an order. |
| cluster2 | Analyzing student demographics, faculty details, course offerings, campus fees, student activities, department statistics, and enrollment data across various colleges and universities. | 436 | What are the different cities where students live? |
| cluster3 | Discover high-quality wines, music, arts, and entertainment data including artists, tracks, genres, albums, films, musicals, exhibitions, festivals, and various related statistics. | 235 | Find the white grape used to produce wines with scores above 90. |
| cluster4 | Retrieve various statistics, counts, and information about various entities, such as departments, budgets, customers, industries, employees, events, and more. | 203 | Give the name of the department with the lowest budget. |
| cluster5 | Analyze various data including demographics, capacities, enrollments, industries, and statistics to obtain insights about airports, cities, companies, departments, colleges, events, and various entities. | 479 | What is the average and total capacity for all dorms who are of gender X? |
| cluster6 | Explore information on airlines, airports, cities, countries, train stations, tourist attractions, colleges, dorms, apartments, companies, employees, bank branches, hotels, rooms, regional populations, store districts, factories, transportation methods, and various statistics. | 339 | Find the number of routes operated by American Airlines. |
| cluster7 | Analyze various customer, employee, product, and transaction data for insights on accounts, balances, payments, invoices, loans, complaints, orders, salaries, and various other details. | 417 | What are the last names of customers without invoice totals exceeding 20? |
| cluster8 | Retrieve and analyze various data: counties, schools, apartments, ministers, populations, businesses, memberships, flights, events, railways, cities, records, and more. | 311 | Show the names of counties that have at least two delegates. |
| cluster9 | Analyze and summarize data across various categories such as product details, user roles, company statistics, project information, and employee records. | 397 | What are the code and description of the most frequent behavior incident type? |


## Ideas for Improvement
Overall I believe this setup represents a respectable baseline, but there are a few areas that I think could be improved on:

### Fine-tuning to optimize query representation
The dataset we are given includes SQL queries corresponding to each of the natural language queries. If we fine-tune our encoder model on the seq2seq task of predicting the SQL translation given the English query, the representations we extract for clustering will be optimized representations of the text which predict the explicit, functional intent of the query. My intuition around text representation makes me think this could be better-suited for our task, which is to discover the types of intents people are trying to convey through their prose, and avoids us having to wade through possible noise of a natural language interface. 

An example of this is how many of the clusters are aligned according to simple lexical overlap, especially in the use of syntactic constructions used to form questions. The "What is"s dominate a few clusters while the "Show me/list the"s are also found together. This suggests that lexical overlap and certain syntactic constructions are strong features emerging from our representation choice. Fine-tuning on a task that focuses on optimizing a representation of the _intent_ of the query, rather than the _form_ would likely mitigate this effect.

### Evaluation of cluster quality
The scope of this project meant that my evaluation of cluster quality was restricted to browsing the clusters manually to make sure that the results were reasonable. Given a bit more time, it would be useful to implement some intrinsic and extrinsic measures of cluster quality. For example:

- <b>Intrinsic evaluation</b>: we could calculate the cluster cardinality (# of examples per cluster) and cluster magnitude (sum of distances of each point in a cluster from its centroid). We could observe anomalies in these two metrics individually, and also plot the magnitude over cardinality and spot clusters whose correlation is anomalous relative to the other clusters. 
- <b>Extrinsic Evaluation</b>: assuming the clusters are consumed as features for some downstream model or system, we could measure the performance delta between different runs of the clustering model to determine which configuration has the optimal intended effect.