from flask import Flask
#from flask_restful import Resource, Api

app = Flask(__name__)

@app.route('/hello')
def web_run():
	return 'hi'
#    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
#    parser.add_argument("config" , nargs="+", help="Path to YAML config file")
#    args = parser.parse_args()
#    main(args.config)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)	