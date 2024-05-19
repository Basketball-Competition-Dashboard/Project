from flask import Flask, render_template


app = Flask(
    __name__,
    static_url_path="/",
    static_folder="web/dist",
    template_folder="web/dist",
)
app.secret_key = "coffee.db"


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
