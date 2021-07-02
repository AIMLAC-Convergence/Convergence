from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from flask import Flask
import os
import yaml
from fill_df import *

def main(config):

    with open(config[0]) as file:
         content = yaml.load(file, Loader=yaml.FullLoader)
         params = content['params']
    keys = ['apikey','location']
    for key in keys:
        try:
            params[key]
        except KeyError:
            print(f'KeyError! Must provide: {key}')
            exit()
    
    df = fill_df(params)
    
    app = Flask(__name__)
    @app.route("/")
    def generate_buzz():
        page = '<html><body><h1>'
        page += df.to_html()
        page += '</h1></body></html>'
        return page
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    
if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
    args = parser.parse_args()
    main(args.config)
