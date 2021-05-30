import csv
from datetime import date
import numpy as np
import operator
import matplotlib.pyplot as plt
import nltk as nltk
import pandas as pd
import scipy.stats as ss
from top2vec import Top2Vec
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.dates as mdates
from fpdf import FPDF
import datetime
import json
import statistics
import torch
from numba import cuda
import openai
from jsonlines import jsonlines

nltk.download('wordnet')
wnl = nltk.WordNetLemmatizer()
print(wnl.lemmatize('earphones'))
torch.cuda.empty_cache()

plt.style.use('seaborn')  # pretty matplotlib plots
plt.rcParams['figure.figsize'] = (12, 8)  # more matplotlib stuff

# declaring variables
candidate_labels = ['price', 'durable', 'easy', 'quality']
empty_list = []
whole_review_sentiment = []
whole_reviews = []
whole_review_date = []
whole_review_category = []
mean_sentiment = 0

print(
    '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 0 Unsupervised Category @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

with open('data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader, None)  # skips headers
    for row in csv_reader:  # going through reviews data
        if row != empty_list:  # makes sure there isn't and empty row
            whole_reviews.append(str(row[1]))  # adding the whole review to the list
            whole_review_date.append(str(row[2]))  # adding that review date to the list

#  whole_reviews = np.array(whole_reviews)
#whole_reviews_top2 = whole_reviews * 10
# running unsupervised model and generating word cloud
unsupervised_model = Top2Vec(whole_reviews, min_count=10, embedding_model='universal-sentence-encoder')
# runs model and gets topics from sentence list
topic_words, word_scores, topic_nums = unsupervised_model.get_topics(unsupervised_model.get_num_topics())

print(topic_words[0])
for word_index in range(0, len(topic_words[0])):  # gets rid of plural words
    topic_words[0, word_index] = wnl.lemmatize(topic_words[0, word_index])
print(topic_words[0])
# gets the topics that were found in the line above
candidate_labels = candidate_labels + (
    topic_words[0, 0:5]).tolist()  # change number here to include more unsupervised topics
print(candidate_labels)

device = cuda.get_current_device()  # getting current device (GPU)
device.reset()  # resetting to be able to reallocate memory

# importing models
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli", device=0)
analyzer = SentimentIntensityAnalyzer()

# making topic dictionary for later use in zero-shot
sen_topic_dict = {}
for label in candidate_labels:
    sen_topic_dict[label] = [], [], [], [], [], [], [], [], [], []

print(sen_topic_dict)

print(
    '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 1 Category @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

# running model 1, topic analysis
with open('data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader, None)  # skips headers
    for row in csv_reader:  # going through reviews data
        if row != empty_list:  # makes sure there isn't and empty row
            whole_review_sentiment.append(analyzer.polarity_scores(row[1])['compound'])
            whole_classified_dict = classifier(row[1],
                                               candidate_labels)  # runs zero-shot classifier models on whole review
            topic_categories = whole_classified_dict.get('labels')  # gets the labels (categories) from dictionary
            whole_topic_scores = whole_classified_dict.get(
                'scores')  # gets the scores from the dictionary produced by running the model again
            whole_max_score_index, whole_review_max_value = max(enumerate(whole_topic_scores), key=operator.itemgetter(
                1))  # finds the max score of the model output scores
            print("whole review topic " + str(topic_categories[whole_max_score_index]))
            whole_review_category.append(topic_categories[whole_max_score_index])
            sequence_to_classify = nltk.tokenize.sent_tokenize(row[1])
            for sen in sequence_to_classify:  # going through individual review sentences
                classified_dict = classifier(sen, candidate_labels)  # runs zero-shot classifier models on sentence
                topic_scores = classified_dict.get(
                    'scores')  # gets the scores from the dictionary produced by running the model again
                max_score_index, value = max(enumerate(topic_scores), key=operator.itemgetter(
                    1))  # finds the max score of the model output scores
                print(topic_categories[max_score_index])
                sen_topic_dict[topic_categories[max_score_index]][0].append(sen)  # adds values from csv to dictionary
                sen_topic_dict[topic_categories[max_score_index]][2].append(row[2])  # date
                sen_topic_dict[topic_categories[max_score_index]][3].append(row[3])  # variant
                sen_topic_dict[topic_categories[max_score_index]][4].append(row[4])  # images
                sen_topic_dict[topic_categories[max_score_index]][5].append(row[5])  # verified
                sen_topic_dict[topic_categories[max_score_index]][6].append(row[6])  # author
                sen_topic_dict[topic_categories[max_score_index]][7].append(row[7])  # rating
                sen_topic_dict[topic_categories[max_score_index]][8].append(row[8])  # product
                sen_topic_dict[topic_categories[max_score_index]][9].append(row[9])  # url

print(
    '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 2 Sentiment @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

for key, dict_list_list in sen_topic_dict.items():  # loops through items in the main sentence dictionary
    sen_list = dict_list_list[0]  # getting sentences from 2D array
    for sen in sen_list:
        sent_score = analyzer.polarity_scores(sen)['compound']  # gets the compounded sentiment score
        print('sent_score: ' + str(sent_score))
        sen_topic_dict[key][1].append(sent_score)  # adds sentient score to dictionary array

print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Plotting @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

# List for DFs
dfs = []

# Loop through dictionary and create 1 DataFrame per category
for key in sen_topic_dict.keys():
    if len(sen_topic_dict[key][0]) > 0:
        dfs.append(pd.DataFrame({
            "sentence": sen_topic_dict[key][0],
            "score": sen_topic_dict[key][1],
            "date": sen_topic_dict[key][2],
            "variant": sen_topic_dict[key][3],
            "images": sen_topic_dict[key][4],
            "verified": sen_topic_dict[key][5],
            "author": sen_topic_dict[key][6],
            "rating": sen_topic_dict[key][7],
            "product": sen_topic_dict[key][8],
            "url": sen_topic_dict[key][9],
            "category": key
        }))

# Combine DFs
df = pd.concat(dfs, ignore_index=True)
df['date'] = pd.to_datetime(df['date'], format='%d %b %Y')

# Rounding all values

df['score'] = df['score'].round(decimals=3)


def plot_normal(x_range, mu=0, sigma=1, cdf=False, **kwargs):
    """
    Plots the normal distribution function for a given x range
    If mu and sigma are not provided, standard normal is plotted
    If cdf=True cumulative distribution is plotted
    Passes any keyword arguments to matplotlib plot function
    """
    x_val = x_range
    if cdf:
        normal_y = ss.norm.cdf(x_val, mu, sigma)  # change sigma
    else:
        normal_y = ss.norm.pdf(x_val, mu, sigma)  # change sigma

    plt.plot(x_val, normal_y, **kwargs)
    plt.legend('stars', 'sentiment')


# plotting star and sentiment distributions
star_list = df.rating.tolist()  # makes a list from the rating column
for i in range(0, len(star_list)):  # goes through each item in list
    star_list[i] = float(star_list[i])  # turning star ratings into a float
df.rating = star_list  # reassigning the float star list to the rating column in main df

normalized_star_data = []
for rating in star_list:
    normalized_star_data.append(((1 + 1) / (5 - 1)) * (rating - 5) + 1)

star_mean = statistics.mean(star_list)
normalized_star_stdv = statistics.stdev(normalized_star_data)
normalized_star_mean = ((1 + 1) / (5 - 1)) * (star_mean - 5) + 1

sent_list = df.score.tolist()  # makes a list of sent scores
for i in range(0, len(sent_list)):  # goes through each item in list
    sent_list[i] = float(sent_list[i])  # turning each sentiment score into a float

normalized_mean_sentiment = statistics.mean(sent_list)
normalized_stdv_sentiment = statistics.stdev(sent_list)
mean_sentiment = ((5 - 1) / (1 + 1)) * (normalized_mean_sentiment - 1) + 5

star_scale_sentiments = []
for sentiment in df.score:
    star_scale_sentiments.append(int(((5 - 1) / (1 + 1)) * (sentiment - 1) + 5))

df['star_scale_sentiments'] = star_scale_sentiments

# making review rating distributions data for plotting
print("star mean: " + str(normalized_star_mean))
print("star stdv: " + str(normalized_star_stdv))
print("sentiment mean: " + str(normalized_mean_sentiment))
print("sentiment stdv: " + str(normalized_stdv_sentiment))

# making sentiment per category data for plotting
plotDfCategory = df.groupby(['category'], as_index=False).mean().round(3)
plotDfCategory.score / len(df.score)
max_category_index, max_cat_value = max(enumerate(plotDfCategory.score), key=operator.itemgetter(1))
min_category_index, min_cat_value = min(enumerate(plotDfCategory.score), key=operator.itemgetter(1))

# making star and ratings distribution graphs for website, not to be confused for the normal distributions
distributionStarDf = df.groupby(['rating'], as_index=False).count()
distributionStarDf.add_suffix('_Count').reset_index()
distributionScoreDf = df.groupby(['star_scale_sentiments'], as_index=False).count()
distributionScoreDf.add_suffix('_Count').reset_index()

# making trend data for plotting
plotDfTrendline = df.groupby(['date'], as_index=False).mean().round(
    3)  # groups by date and takes the mean of the scores
df = df.sort_values('date')

# making df for plotting variance and sentiment
plot_df_variant = df.groupby(['variant'], as_index=False).mean().round(3)
plot_df_variant.add_suffix('_Mean').reset_index()  # converts groupby object back to dataframe
plot_df_variant_star = plot_df_variant

if len(plot_df_variant.variant) > 10:  # if there are more then 10 variants, concatenates the lists
    nlargestScore = plot_df_variant.nlargest(5, 'score')
    nsmallestScore = plot_df_variant.nsmallest(5, 'score')
    plot_df_variant = [nlargestScore, nsmallestScore]  # merging score lists
    nlargestRating = plot_df_variant_star.nlargest(5, 'rating')
    nsmallestRating = plot_df_variant_star.nsmallest(5, 'rating')
    plot_df_variant_star = [nlargestRating, nsmallestRating]  # merging ratings list

    plot_df_variant = pd.concat(plot_df_variant).reset_index()  # turning list into dataframe
    plot_df_variant_star = pd.concat(plot_df_variant_star).reset_index()  # turning list into dataframe

max_variant_sentiment_index, max_variant_sentiment_value = max(enumerate(plot_df_variant.score),
                                                               key=operator.itemgetter(1))
min_variant_sentiment_index, min_variant_sentiment_value = min(enumerate(plot_df_variant.score),
                                                               key=operator.itemgetter(1))
max_variant_star_index, max_variant_star_value = max(enumerate(plot_df_variant_star.rating),
                                                     key=operator.itemgetter(1))
min_variant_star_index, min_variant_star_value = min(enumerate(plot_df_variant_star.rating),
                                                     key=operator.itemgetter(1))

print(plot_df_variant)
print(plot_df_variant_star)

# finding net promoter score
promoters = []
detractors = []
neutrals = []
for sentiment in df.score:
    promoter_score = ((10 - 0) / (1 + 1)) * (sentiment - 1) + 10
    if 0 <= promoter_score <= 6:
        detractors.append(promoter_score)
    elif 9 <= promoter_score <= 10:
        promoters.append(promoter_score)
    else:
        neutrals.append(promoter_score)
print(promoters)
print(detractors)
print(neutrals)
net_promoter_score = (len(promoters) / len(df.score)) - (len(detractors) / len(df.score))

print('net promoter score', net_promoter_score)

# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = 'Comic Sans MS'

# now the actual plotting begins
# SENTIMENT PER CATEGORY
plt.grid(False)
plotDfCategory['positive'] = plotDfCategory['score'] > 0
plt.barh(plotDfCategory.category, plotDfCategory.score, color=plotDfCategory.positive.map({True: 'g', False: 'r'}))
plt.title('Sentiment Per Category', fontsize=20, fontweight='bold')
plt.ylabel('Categories', fontsize=20, fontweight='bold')
# plt.xticks([-1, 0, 1], [":(", ":|", ":)"], fontsize=20, fontweight='bold')
plt.yticks(fontsize=20)
plt.xticks(fontsize=20)
plt.savefig('plot1.png')
plt.close()
# plt.show()

x = np.linspace(-1.5, 1.5, 5000)

# NORMAL PLOTS
plot_normal(x, normalized_star_mean, normalized_star_stdv, color='red', lw=2, ls='-', alpha=0.5, label='star')
plot_normal(x, normalized_mean_sentiment, normalized_stdv_sentiment, color='blue', lw=2, ls='-', alpha=0.5,
            label='sentiment')
plt.grid(False)
plt.title('Sentiment Per Category', fontsize=20, fontweight='bold')
plt.ylabel('Categories', fontsize=20, fontweight='bold')
plt.xticks([-1, 0, 1], [":(", ":|", ":)"], fontsize=20, fontweight='bold')
plt.title('Distributions of Sentiment vs Star Rating', fontsize=20, fontweight='bold')
plt.xlabel('Sentiment', fontsize=20, fontweight='bold')
plt.ylabel('Frequency', fontsize=20, fontweight='bold')
plt.yticks(fontsize=20)
plt.savefig('plot2.png')
plt.close()
# plt.show()

# TRENDLINE
plt.grid(False)
xdate = plotDfTrendline.date.apply(lambda x: x.strftime('%Y-%m-%d'))
y = plotDfTrendline.score
plt.plot(xdate, y)  # plots date sentiment graph
x2 = mdates.date2num(xdate)  # for trendline turn into datetime object
z = np.polyfit(x2, y, 1)
slope = (z[0])
p = np.poly1d(z)
plt.plot(xdate, p(x2), 'r--')  # add trendline to plot
plt.title('Product Sentiment Trend Over Time', fontsize=20, fontweight='bold')
plt.xlabel('Time', fontsize=20, fontweight='bold')
plt.yticks([-1, 0, 1], [":(", ":|", ":)"], fontsize=20, fontweight='bold')
plt.xticks(fontsize=20)
plt.savefig('plot3.png')
plt.close()
json_trendline_regression = json.dumps([{'x': date, 'y': score} for date, score in zip(xdate, p(x2).round(3))],
                                       default=str)
json_trendline_regression = json.loads(json_trendline_regression)
# plt.show()

# STAR TRENDLINE
plt.grid(False)
y = plotDfTrendline.rating
plt.plot(xdate, y)  # plots date sentiment graph
x2 = mdates.date2num(xdate)  # for trendline turn into datetime object
z = np.polyfit(x2, y, 1)
slope_star = (z[0])
p = np.poly1d(z)
plt.plot(xdate, p(x2), 'r--')  # add trendline to plot
plt.title('Product Star Rating Trend Over Time', fontsize=20, fontweight='bold')
plt.xlabel('Time', fontsize=20, fontweight='bold')
plt.xticks(fontsize=20)
plt.savefig('plot3star.png')
plt.close()
json_trendline_rating_regression = json.dumps([{'x': date, 'y': rating} for date, rating in zip(xdate, p(x2).round(3))],
                                              default=str)
json_trendline_rating_regression = json.loads(json_trendline_rating_regression)
# plt.show()

# 1 YEAR TRENDLINE
base = max(plotDfTrendline.date)  # setting base date to the date that is closest to today
one_year_ago_today = base - datetime.timedelta(days=365)
one_year_ago_df = plotDfTrendline[plotDfTrendline['date'] > one_year_ago_today]
plt.grid(False)
y = one_year_ago_df.score
xdate = one_year_ago_df.date  # xdate here is of type timestamp
plt.plot(xdate, y)  # plots date sentiment graph
x2 = mdates.date2num(xdate)  # for trendline turn into datetime object
z = np.polyfit(x2, y, 1)
slope_oneyear = (z[0])
p = np.poly1d(z)
plt.plot(xdate, p(x2), 'r--')  # add trendline to plot
plt.title('Product Sentiment Trend Over 1 Year', fontsize=20, fontweight='bold')
plt.xlabel('Time', fontsize=20, fontweight='bold')
plt.yticks([-1, 0, 1], [":(", ":|", ":)"], fontsize=20, fontweight='bold')
plt.xticks(fontsize=20)
plt.xlim(one_year_ago_today, base)
plt.savefig('plot3_oneYear.png')
plt.close()
date_time_xdate = xdate.apply(lambda x: x.strftime('%Y-%m-%d'))
json_trendline_regression_one_year = json.dumps(
    [{'x': date, 'y': score} for date, score in zip(date_time_xdate, p(x2).round(3))], default=str)
json_trendline_regression_one_year = json.loads(json_trendline_regression_one_year)
# plt.show()

# SENTIMENT PER VARIANT
plt.grid(False)
plt.title('Sentiment Per Varient', fontsize=20, fontweight='bold')
plot_df_variant['positive'] = plot_df_variant['score'] > 0
plt.barh(plot_df_variant.variant, plot_df_variant.score, color=plot_df_variant.positive.map({True: 'g', False: 'r'}))
plt.xticks([-1, 0, 1], [":(", ":|", ":)"], fontsize=20, fontweight='bold')
plt.xlim([-1, 1])
plt.savefig('plot4.png')
plt.close()

# STAR PER VARIANT
plt.grid(False)
plt.title('Star Per Variant', fontsize=20, fontweight='bold')
plot_df_variant_star['positive'] = plot_df_variant_star['rating'] > 0
plt.barh(plot_df_variant_star.variant, plot_df_variant_star.rating,
         color=plot_df_variant_star.positive.map({True: 'g', False: 'r'}))
plt.savefig('plot4star.png')
plt.close()
# plt.show()

print(topic_nums)
for i in range(0, len(topic_nums)):
    print(i)
    unsupervised_model.generate_topic_wordcloud(i, background_color='white')
    plt.savefig('plot' + str(i + 5) + '.png')
    plt.close()
    # plt.show()

max_index = whole_review_sentiment.index(max(whole_review_sentiment))  # calculated max index for max review
min_index = whole_review_sentiment.index(min(whole_review_sentiment))  # does the same as above but for min review
neutral_index = whole_review_sentiment.index(min(whole_review_sentiment, key=abs))  # same but for neutral review

# save FPDF() class into a
# variable pdf
pdftext = FPDF()
pdftext.add_font('Avenir', '', r"C:\Users\tomcs\Desktop\Metropolis-Medium.ttf", uni=True)
# Add a page
pdftext.add_page()
# Save top coordinate
top = pdftext.y
# set style and size of font
# that you want in the pdf
pdftext.set_font("Avenir", size=15)

# create a cell
pdftext.image('pondr_logo.png', x=10, y=8, w=26, h=14)
pdftext.multi_cell(200, 5, txt='beta version 1.0.2 made on ' + str(date.today()) + '\n\n\n', align='R')
pdftext.multi_cell(200, 5, txt=('Report on ' + df.iloc[1, 8]), align='L')

pdftext.set_font_size(12)
pdftext.multi_cell(200, 5, txt="After analyzing " + str(len(df.score)) + " reviews, here is what we found: " + '\n',
                   align='L')
pdftext.multi_cell(200, 5, txt="Estimated net promoter score " + str(
    int(net_promoter_score * 100)) + ' (this is in testing for accuracy) \n',
                   align='L')
pdftext.set_font_size(8)
pdftext.multi_cell(200, 5, txt="Most talked about topics: " + (
    ', '.join(topic_words[0:(len(topic_words) - 1), 0])).capitalize() + ', and ' + (
                                   topic_words[(len(topic_words) - 1), 0]).capitalize(), align='L')

# pdftext.add_page()

# pdftext.multi_cell(200, 5, txt='put definitions here')

pdftext.add_page()

offset = pdftext.x + 110
pdftext.image('plot1.png', x=10, y=25, w=105, h=80)
pdftext.y = 30
pdftext.x = offset
pdftext.set_font_size(8)

categorySentences = [None] * len(plotDfCategory.category)  # creating an empty list of the size of category
for i in range(0, len(plotDfCategory.category)):
    if 0.1 > plotDfCategory.score[i] > -0.1:
        categorySentences[i] = str(plotDfCategory.category[i] + ': ' + str(
            round(plotDfCategory.score[i], 3)) + ' -- Consumer sentiment towards ' + plotDfCategory.category[i]
                                   + ' is relatively neutral. Consumers are neither dissatisfied or impressed. \n')
    elif plotDfCategory.score[i] < -0.1:
        categorySentences[i] = str(plotDfCategory.category[i] + ': ' + str(
            round(plotDfCategory.score[i], 3)) + ' -- Consumer sentiment towards ' + plotDfCategory.category[
                                       i] + ' is negative. Consumers arent satisfied with the ' +
                                   plotDfCategory.category[i] + ' of your product. \n')
    elif plotDfCategory.score[i] > 0.1:
        categorySentences[i] = str(plotDfCategory.category[i] + ': ' + str(
            round(plotDfCategory.score[i], 3)) + ' -- Consumer sentiment towards ' + plotDfCategory.category[
                                       i] + ' is positive. Consumers are satisfied with the ' +
                                   plotDfCategory.category[i] + ' of your product! \n')

pdftext.multi_cell(75, 5, ''.join(categorySentences), align='L')

offset = pdftext.x + 110
pdftext.image('plot4.png', x=10, y=100, w=105, h=80)
pdftext.y = 110
pdftext.x = offset
if len(plot_df_variant.variant) <= 1:
    pdftext.multi_cell(75, 5, 'This graph displays customer sentiment per product variant. However, this product only '
                              'has one variant which has an average sentiment score of ' + str(
        round(plot_df_variant.score[0], 3)), align='L')
else:
    pdftext.multi_cell(75, 5,
                       'This graph displays customer sentiment per product variant. Of the customers who reviewed '
                       'this product, they prefered the ' + plot_df_variant.variant[max_variant_sentiment_index] +
                       ' variant and disliked the ' + plot_df_variant.variant[min_variant_sentiment_index] + ' variant',
                       align='L')

offset = pdftext.x + 110
pdftext.image('plot4star.png', x=10, y=175, w=105, h=80)
pdftext.y = 185
pdftext.x = offset
if len(plot_df_variant_star.variant) <= 1:
    pdftext.multi_cell(75, 5,
                       'This graph displays customer star rating per product variant. However, this product only '
                       'has one variant which has an average star rating of ' + str(
                           round(plot_df_variant_star.rating[0], 3)), align='L')
else:
    pdftext.multi_cell(75, 5,
                       'This graph displays customer star rating per product variant. Of the customers who reviewed '
                       'this product, they prefered the ' + plot_df_variant_star.variant[max_variant_star_index] +
                       ' variant and disliked the ' + plot_df_variant_star.variant[min_variant_star_index] + ' variant',
                       align='L')

pdftext.add_page()

offset = pdftext.x + 110
pdftext.image('plot2.png', x=10, y=25, w=105, h=80)
pdftext.y = 35
pdftext.x = offset
if normalized_star_mean > normalized_mean_sentiment:
    pdftext.multi_cell(75, 5,
                       'This graph displays the distribution of sentiment scores (blue) vs user star rating (red). This means that of the reviews written, customers rated this product higher then they wrote their review \n your average star rating is ' + str(
                           round(star_mean, 3)) + ' out of five ' + ' \n your average sentiment rating is ' + str(
                           round(mean_sentiment, 3)) + ' out of five ',
                       align='L')
elif normalized_star_mean < normalized_mean_sentiment:
    pdftext.multi_cell(75, 5,
                       'This graph displays the distribution of sentiment scores (blue) vs user star rating (red). This means that of the reviews written, customers rated this product lower then they wrote their review \n your average star rating is ' + str(
                           round(star_mean, 3)) + ' out of five ' + ' \n your average sentiment rating is ' + str(
                           round(mean_sentiment, 3)) + ' out of five ',
                       align='L')

offset = pdftext.x + 110
pdftext.image('plot3.png', x=10, y=100, w=105, h=80)
pdftext.y = 110
pdftext.x = offset
print('type of slope ', type(slope))
if slope < 0:  # fix this situation
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer sentiment over time. The trendline helps illustrate this trend. This product has a negative slope and is therefore trending downwards',
                       align='L')
elif slope > 0:
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer sentiment over time. The trendline helps illustrate this trend. This product has a positive slope and is therefore trending upwards',
                       align='L')

offset = pdftext.x + 110
pdftext.image('plot3star.png', x=10, y=175, w=105, h=80)
pdftext.y = 185
pdftext.x = offset
print('type of slope ', type(slope_star))
if slope_star < 0:  # fix this situation
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer star rating over time. The trendline helps illustrate this trend. This product has a negative slope and is therefore trending downwards',
                       align='L')
elif slope_star > 0:
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer star rating over time. The trendline helps illustrate this trend. This product has a positive slope and is therefore trending upwards',
                       align='L')

pdftext.add_page()

offset = pdftext.x + 110
pdftext.image('plot3_oneYear.png', x=10, y=25, w=105, h=80)
pdftext.y = 35
pdftext.x = offset
print('type of slope ', type(slope_oneyear))
if slope_oneyear < 0:  # fix this situation
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer sentiment over a one year time spand. The trendline helps illustrate this trend. This product has a negative slope and is therefore trending downwards during this time period',
                       align='L')
elif slope_oneyear > 0:
    pdftext.multi_cell(75, 5,
                       'The graph above represents consumer sentiment over a one year time spand. The trendline helps illustrate this trend. This product has a positive slope and is therefore trending upwards during this time period',
                       align='L')

text_y = 110
image_y = 120
for word_cloud_index in range(0, len(topic_nums)):
    pdftext.y = text_y
    pdftext.x = 10
    pdftext.multi_cell(75, 5, ('This is the word cloud for ' + str(topic_words[word_cloud_index][0])), align='L')
    pdftext.image(('plot' + str(word_cloud_index + 5) + '.png'), x=0, y=image_y, w=200, h=50)
    text_y = text_y + 65
    image_y = image_y + 65
    if text_y > 240:
        pdftext.add_page()
        text_y = 10
        image_y = 20

pdftext.add_page()

pdftext.set_font("Avenir", size=15)
pdftext.multi_cell(200, 5, txt='Reviews\n', align='C')
pdftext.set_font("Avenir", size=12)
pdftext.set_text_color(9, 255, 0)
pdftext.multi_cell(200, 5, txt='Best Review :) \n' + whole_reviews[max_index] + '\n', align='L')
pdftext.set_text_color(252, 3, 3)
pdftext.multi_cell(200, 5, txt='Worst Review :(  \n' + whole_reviews[min_index] + '\n', align='L')
pdftext.set_text_color(255, 230, 0)
pdftext.multi_cell(200, 5, txt='Most Neutral Review :| \n' + whole_reviews[neutral_index] + '\n', align='L')
pdftext.y = 270
pdftext.set_text_color(0, 0, 0)
pdftext.multi_cell(200, 5, txt='www.letspondr.com', align='C')

# pdftext.add_page()

# pdftext.set_text_color(0, 0, 0)
# pdftext.set_font("Avenir", size=15)
# pdftext.multi_cell(200, 5, txt='GPT Review Summary\n', align='C')
# pdftext.set_font("Avenir", size=12)
# gpt_output = open("gpt2output.txt", "r")
# for line in gpt_output:
#    print(line)
#    pdftext.multi_cell(200, 5, txt=line + '\n', align='L')

# save the pdf with name .pdf
pdftext.output('Report.pdf')

plotDfTrendline['y'] = plotDfTrendline['score']
plotDfTrendline['x'] = plotDfTrendline['date'].apply(
    lambda x: x.strftime('%Y-%m-%d'))  # turing date time object to strings to appear correct in json
result = plotDfTrendline[['x', 'y']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_date_score = parsed

plotDfTrendline['y'] = plotDfTrendline['rating']
result = plotDfTrendline[['x', 'y']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_date_rating = parsed

result = plotDfCategory.iloc[:, 0:2].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_category = parsed

result = plot_df_variant[['variant', 'score']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_variant_score = parsed

result = plot_df_variant_star[['variant', 'rating']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_variant_rating = parsed

result = distributionStarDf[['rating', 'sentence']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_star_distribution = parsed
print(json_star_distribution)

result = distributionScoreDf[['star_scale_sentiments', 'sentence']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_score_distribution = parsed
print(json_score_distribution)

one_year_ago_df['x'] = one_year_ago_df['date'].apply(
    lambda x: x.strftime('%Y-%m-%d'))  # turing date time object to strings to appear correct in json
one_year_ago_df['y'] = one_year_ago_df['score']
result = one_year_ago_df[['x', 'y']].to_json(orient="records")
parsed = json.loads(result)
json.dumps(parsed, indent=4)
json_date_one_year = parsed

full_cat_json = {}
whole_review_sentiment = [round(elem, 3) for elem in whole_review_sentiment]

for label in candidate_labels:
    full_cat_json[label] = []
for i in range(0, len(whole_reviews) - 1):
    full_cat_json[whole_review_category[i]].append(
        {"date": whole_review_date[i], "score": whole_review_sentiment[i], "review": whole_reviews[i]})
full_cat_json = json.dumps(full_cat_json, indent=1)
full_cat_json = json.loads(full_cat_json)
print("full cat df " + str(type(full_cat_json)))

# Open AI file upload

openai.api_key = ("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")

file_name = "gpt3training.txt"

with open(file_name) as f:
    mylist = f.read().splitlines()

json_to_upload = json.dumps([{'text': test} for test in mylist], default=str, indent=1)
json_to_upload = json.loads(json_to_upload)
print(type(json_to_upload))
# json_to_upload = json.dumps([{'text': mylist}], default=str, indent=1)
# json_to_upload = json.loads(json_to_upload)

with jsonlines.open('upload.jsonl', mode='w') as writer:
    for entry in json_to_upload:
        writer.write(entry)

upload = openai.File.create(
    file=open("upload.jsonl"),
    purpose='answers'
)

print(upload['id'])

package = {
    "data": {
        "product_id": "Cvw8d65PQTykN2i3YHdE",
        "company_id": "y4X15yERWulGWueGa1Xc",
        "product_name": df.iloc[1, 8],
        "1": {
            "title": "Sentiment per category",
            "description": "This is a graph of sentiment per category...",
            "sentiment_per_category": json_category
        },
        "2": {
            "title": "Sentiment per variant",
            "description": "This is the graph for product sentiment per product variant",
            "sentiment_per_variant": json_variant_score
        },
        "3": {
            "title": "Distributions of sentiment",
            "description": "This is the plot of distributions of the sentiment rating of this product ",
            "distributions_of_sentiment": json_star_distribution

        },
        "4": {
            "title": "Distributions of star rating",
            "description": "this is the plot of the distributions of the star ratings of this product ",
            "distributions_of_star": json_score_distribution
        },
        "5": {
            "title": " line graphs",
            "description1": "this is the trendline plot for this product's sentiment for all time",
            "product_trend_all": {
                "regression_line": json_trendline_regression,
                "points": json_date_score
            },

            "description2": "this is the trendline plot for this product's sentiment for one year",
            "product_trend_1year": {
                "regression_line": json_trendline_regression_one_year,
                "points": json_date_one_year
            },

            "description3": "this is the trendline plot for this product's star rating for all time",
            "product_trend_all_star": {
                "regression_line": json_trendline_rating_regression,
                "points": json_date_rating
            }
        },
        "summary": {
            "nps": net_promoter_score,
            "num_of_reviews": str(len(whole_reviews)),
            "topics": (', '.join(topic_words[0:(len(topic_words) - 1), 0])).capitalize() + ', and ' + (
                topic_words[(len(topic_words) - 1), 0]).capitalize(),
            "date": str(date.today()),
            "category_data": upload['id']
        },
        "gpt3_form_id": "test",

        "review_types": {
            "best_review": whole_reviews[max_index],
            "worst_review": whole_reviews[min_index],
            "neutral": whole_reviews[neutral_index]
        },
        "word_cloud": "null"
    }
}

with open('package.json', 'w') as json_file:
    json.dump(package, json_file)

print(package)
