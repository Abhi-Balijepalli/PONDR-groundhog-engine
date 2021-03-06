import os
import json
import statistics
from datetime import date
import matplotlib.dates as mdates
import nltk as nltk
import numpy as np
import openai
import pandas as pd
import torch
from jsonlines import jsonlines
from numba import cuda
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deals_post import send_deals_data

openai.api_key = "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"
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
today = date.today()


def run_deals(raw_review_data, gpt3_data, id_num, price, product_images, short_description, long_description, category, asin, type):
    nltk.download('wordnet')
    nltk.download('punkt')
    wnl = nltk.WordNetLemmatizer()
    torch.cuda.empty_cache()

    # declaring variables
    candidate_labels = ['price', 'durable', 'easy', 'quality']
    empty_list = []
    whole_review_sentiment = []
    whole_reviews = []
    whole_review_date = []
    review_data = []

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 0 Unsupervised Category @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # transforming list of dictionaries into 2d list
    for raw_row in raw_review_data:  # going through reviews data
        if raw_row != empty_list:  # makes sure there isn't and empty row
            review_data.append(list(raw_row.values()))

    device = cuda.get_current_device()  # getting current device (GPU)
    device.reset()  # resetting to be able to reallocate memory

    # importing models

    analyzer = SentimentIntensityAnalyzer()

    # making topic dictionary for later use in zero-shot
    sen_topic_dict = {}
    sen_topic_dict['None'] = [], [], [], [], [], [], [], [], [], [], [], []

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 1 Category @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # num_of_cats_done = 0
    # running model 1, topic analysis
    for row in review_data:  # going through reviews data
        if row != empty_list and row[1] != "":  # makes sure there isn't and empty row
            sequence_to_classify = nltk.tokenize.sent_tokenize(row[1])
            whole_reviews.append(row[1])
            whole_review_sentiment.append(analyzer.polarity_scores(row[1])['compound'])
            for sen in sequence_to_classify:  # going through individual review sentences
                topic_categories = 'None'

                sen_topic_dict[topic_categories][0].append(sen)  # adds values from csv to dictionary
                sen_topic_dict[topic_categories][2].append(row[2])  # date
                sen_topic_dict[topic_categories][3].append(row[3])  # variant
                sen_topic_dict[topic_categories][4].append(row[4])  # images
                sen_topic_dict[topic_categories][5].append(row[5])  # verified
                sen_topic_dict[topic_categories][6].append(row[6])  # author
                sen_topic_dict[topic_categories][7].append(row[7])  # rating
                sen_topic_dict[topic_categories][8].append(row[8])  # product
                sen_topic_dict[topic_categories][9].append(row[9])  # url

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Model 2 Sentiment @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

    for key, dict_list_list in sen_topic_dict.items():  # loops through items in the main sentence dictionary
        sen_list = dict_list_list[0]  # getting sentences from 2D array
        for sen in sen_list:
            sent_score = analyzer.polarity_scores(sen)['compound']  # gets the compounded sentiment score
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
                "category": key,
                # "emotion": sen_topic_dict[key][10],
                # "emotion_percentage": sen_topic_dict[key][11]
            }))

    # Combine DFs
    df = pd.concat(dfs, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'], format='%d %b %Y')

    # Rounding all values
    df['score'] = df['score'].round(decimals=3)
    print(df)

    star_list = df.rating.tolist()  # makes a list from the rating column
    for i in range(0, len(star_list)):  # goes through each item in list
        star_list[i] = float(star_list[i])  # turning star ratings into a float
    df.rating = star_list  # reassigning the float star list to the rating column in main df

    normalized_star_data = []
    for rating in star_list:
        normalized_star_data.append(((1 + 1) / (5 - 1)) * (rating - 5) + 1)
    star_mean = statistics.mean(star_list)

    sent_list = df.score.tolist()  # makes a list of sent scores
    for i in range(0, len(sent_list)):  # goes through each item in list
        sent_list[i] = float(sent_list[i])  # turning each sentiment score into a float
    normalized_mean_sentiment = statistics.mean(sent_list)

    star_scale_sentiments = []
    for sentiment in df.score:
        star_scale_sentiments.append(int(round(((5 - 1) / (1 + 1)) * (sentiment - 1) + 5)))

    df['star_scale_sentiments'] = star_scale_sentiments

    # making review rating distributions data for plotting
    # making sentiment per category data for plotting

    # making star and ratings distribution graphs for website, not to be confused for the normal distributions
    distributionStarDf = df.groupby(['rating'], as_index=False).count()
    distributionStarDf.add_suffix('_Count').reset_index()
    distributionScoreDf = df.groupby(['star_scale_sentiments'], as_index=False).count()
    distributionScoreDf.add_suffix('_Count').reset_index()

    # making trend data for plotting
    # groups by date and takes the mean of the scores
    plotDfTrendline = df.groupby(['date'], as_index=False).mean().round(3)
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

    # TRENDLINE
    xdate = plotDfTrendline.date.apply(lambda x: x.strftime('%Y-%m-%d'))
    y = plotDfTrendline.score
    x2 = mdates.date2num(xdate)  # for trendline turn into datetime object
    z = np.polyfit(x2, y, 1)
    p = np.poly1d(z)

    json_trendline_regression = json.dumps([{'x': date, 'y': score} for date, score in zip(xdate, p(x2).round(3))],
                                           default=str)
    json_trendline_regression = json.loads(json_trendline_regression)

    # STAR TRENDLINE
    y = plotDfTrendline.rating
    x2 = mdates.date2num(xdate)  # for trendline turn into datetime object
    z = np.polyfit(x2, y, 1)
    p = np.poly1d(z)
    json_trendline_rating_regression = json.dumps(
        [{'x': date, 'y': rating} for date, rating in zip(xdate, p(x2).round(3))],
        default=str)
    json_trendline_rating_regression = json.loads(json_trendline_rating_regression)

    # SENTIMENT PER VARIANT
    plot_df_variant['positive'] = plot_df_variant['score'] > 0

    # STAR PER VARIANT
    plot_df_variant_star['positive'] = plot_df_variant_star['rating'] > 0

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

    result = distributionScoreDf[['star_scale_sentiments', 'sentence']].to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    json_score_distribution = parsed

    # Open AI file upload

    mylist = gpt3_data
    json_to_upload = json.dumps([{'text': text} for text in mylist], default=str, indent=1)
    json_to_upload = json.loads(json_to_upload)
    # json_to_upload = json.dumps([{'text': mylist}], default=str, indent=1)
    # json_to_upload = json.loads(json_to_upload)

    with jsonlines.open('upload.jsonl', mode='w') as writer:
        for entry in json_to_upload:
            writer.write(entry)

    upload = {}
    upload['id'] = ""
    while len(upload['id']) < 5:
        try:
            upload = openai.File.create(
                file=open("upload.jsonl"),
                purpose='answers'
            )
        except:
            upload['id'] = ""

    print(upload['id'])
    max_index = whole_review_sentiment.index(max(whole_review_sentiment))  # calculated max index for max review
    min_index = whole_review_sentiment.index(min(whole_review_sentiment))  # does the same as above but for min review

    package = {
        "data": {
            "asin": asin,
            "key": "(#z_3mhQ6xo[$B&",
            "product_name": df.iloc[1, 8],
            "2": {
                "title": "Sentiment Per Variant",
                "description": 'sentiment_variant_description',
                "sentiment_per_variant": json_variant_score
            },
            "3": {
                "title": "Distributions of Star Rating",
                "description": "star_variant_description",
                "distributions_of_sentiment": json_star_distribution
            },
            "4": {
                "title": "Distributions of Sentiment",
                "description": "This is the plot of distributions of the sentiment rating of this product ",
                "distributions_of_star": json_score_distribution
            },
            "5": {
                "title": " line graphs",
                "description1": "This is the trendline plot for this product's sentiment for all time",
                "product_trend_all": {
                    "regression_line": [json_trendline_regression[0], json_trendline_regression[-1]],
                    "points": json_date_score
                },
                "description3": "This is the trendline plot for this product's star rating for all time",
                "product_trend_all_star": {
                    "regression_line": [json_trendline_rating_regression[0], json_trendline_rating_regression[-1]],
                    "points": json_date_rating
                }
            },
            "6": {
                "title": "Rating Per Variant",
                "description": 'sentiment_variant_description',
                "sentiment_per_variant": json_variant_rating
            },
            "summary": {
                "num_of_reviews": int(len(whole_reviews)),
                "date": str(today),
                "mean_sentiment": normalized_mean_sentiment,
                "mean_star_rating": star_mean,
                "images": product_images,
                "price": str(price),
                "short_description": short_description,
                "long_description": long_description,
                "category": str(category),
                "type": type,
                "raw-reviews": json_to_upload
            },
            "gpt3_form_id": upload['id'],

            "review_types": {
                "best_review": whole_reviews[max_index],
                "worst_review": whole_reviews[min_index],
            },
        }
    }

    if int(len(whole_reviews)) > 0:
        with open('package_' + str(id_num) + '.json', 'w') as json_file:
            json.dump(package, json_file)

        send_deals_data(id_num)
