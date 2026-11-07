# app.py
import connexion

app = connexion.FlaskApp(__name__, specification_dir=".")
app.add_api(
    "social_network_openAPI.yaml",
    validate_responses=True,   # handler trả sai spec → 500, dùng để demo
)

if __name__ == "__main__":
    app.run(port=8000)