# importing the requests library
import requests

# defining the api-endpoint
API_ENDPOINT = "http://127.0.0.1:8080/analyze"

# data to be sent to api

# sending post request and saving response as response object
r = requests.post('http://127.0.0.1:8080/analyze', json={
    "data": {
        "product_id": "o7K0Atg791MtbGwkGFer",
        "company_id": "y4X15yERWulGWueGa1Xc",
        "product_name": "Simple Modern Classic Insulated Tumbler with Straw and Flip Lid Stainless Steel Water Bottle Iced Coffee Travel Mug Cup, 20oz (590ml), Midnight Black",
        "1": {
            "title": "Sentiment per category",
            "description": "This is a graph of sentiment per category...",
            "sentiment_per_category": {
                "quality": 0.6,
                "design": -0.33,
                "price": 0.5
            }
        },
        "2": {
            "title": "Sentiment per variant",
            "description": "This is the graph for product sentiment per product variant",
            "sentiment_per_variant": {
                "12oz": 0.3,
                "24oz": -0.45,
                "32oz": 0.13
            }
        },
        "3": {
            "title": "Distributions of sentiment",
            "description": "This is the plot of distributions of the sentiment rating of this product ",
            "distributions_of_senntiment": {
                "1-star": 34,
                "2-star": 12,
                "3-star": 44,
                "4-star": 1,
                "5-star": 12
            }

        },
        "4": {
            "title": "Distributions of star rating",
            "description": "this is the plot of the distributions of the star ratings of this product ",
            "distributions_of_star": {
                "1-star": 12,
                "2-star": 24,
                "3-star": 16,
                "4-star": 11,
                "5-star": 60
            }
        },
        "5": {
            "title": " line graphs",
            "description1": "this is the trendline plot for this product's sentiment for all time",
            "product_trend_all": {
                "regression_line": [{"x": "2020-3-14", "y": 0.3}, {"x": "2020-4-14", "y": 0.4}],
                "points": [{"x": "2020-3-17", "y": 0.7}, {"x": "2020-3-19", "y": 0.4}, {"x": "2020-3-21", "y": -0.7},
                           {"x": "2020-3-29", "y": 0.2}, {"x": "2020-4-4", "y": 0.14}]
            },

            "description2": "this is the trendline plot for this product's sentiment for one year",
            "product_trend_1year": {
                "regression_line": [{"x": "2020-3-14", "y": 0.3}, {"x": "2021-4-14", "y": 0.4}],
                "points": [{"x": "2020-5-17", "y": -0.7}, {"x": "2020-6-19", "y": -0.4}, {"x": "2020-7-21", "y": 0.7},
                           {"x": "2020-10-29", "y": -0.2}, {"x": "2021-4-4", "y": -0.14}]
            },

            "description3": "this is the trendline plot for this product's star rating for all time",
            "product_trend_all_star": {
                "regression_line": [{"x": "2020-3-14", "y": 0.3}, {"x": "2021-4-14", "y": 0.4}],
                "points": [{"x": "2020-5-17", "y": 4}, {"x": "2020-6-19", "y": 4.333}, {"x": "2020-7-21", "y": 3.56},
                           {"x": "2020-10-29", "y": 2.95}, {"x": "2021-4-4", "y": 3.23}]
            }
        },
        "summary": {
            "gpt-3": "gpt-3 summary",
            "nps": "37",
            "num_of_reviews": "2977",
            "topics": "Mug, and On",
            "date": "2021-04-20"
        },

        "review_types": {
            "best_review": "I love this tumbler! I've never really liked the straw cup type cups but I really enjoy this! The design is great, it's sturdy, the straw hole has silicone grip/seal so it isn't wobbling around. I really like that they sent a regular coffee lid as well. I use this mainly for my redbull cream sodas and it's great! I don't like using ice cause it waters it down but it still keeps it cool despite no ice. I have yet to try it for a hot drink but I'm sure it will be great for that too. It's super easy to clean, I can get a sponge down there and easily wipe it out.",
            "worst_review": "Wrong model and sellers pictures need to be corrected for accuracy! Posted 2 pictures: I ordered a Ocean Geode tumbler and a Nebula Tumbler . One order: Ocean Geode where the straw sticks out, i got sent the wrong model with a narrow lid as marked in the picture. I returned it for a replacement and gave in full detail how I got sent the wrong one & that the tumbler shape did not match the picture advertised. Maybe by mistake idk? Got the the replacement and still got the same wrong one. Sent both back. However, I also ordered the Nebula Tumblr as shown on the picture posted which was actually sent right which is the RIGHT model and the other one that was suppose to be sent in the pattern Ocean Geode. Please fix this error and put the right pictures for the right pattern",
            "neutral": "I found this tumbler online while trying to find a way to reduce my single us plastic consumption and actually stick with my previously feeble attempts at staying hydrated. I've had plenty of insulated double-wall tumblers before, but I've NEVER liked one as much as this. I've had it about 7 months now and use it almost every day at work and at home. This thing really stands up to heavy use. I've left cold filtered water in this tumbler in the dead of summer and come back hours later to find it still just as cold as when I poured it. Definitely going to be purchasing in other colors & I've gifted it to a few friends as well."
        },
        "word_cloud": "null"
    }
})

# extracting response text
pastebin_url = r.text

print("The pastebin URL is:%s" % pastebin_url)
