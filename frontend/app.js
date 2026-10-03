const BACKEND_URL = "/api";

async function checkBackend() {

    const statusElement = document.getElementById("backend-status");

    try {

        const response = await fetch(`${BACKEND_URL}/health`);

        if (!response.ok) {
            throw new Error("Backend health check failed");
        }

        const data = await response.json();

        statusElement.textContent =
            `Backend: ${data.status}`;

    } catch (error) {

        statusElement.textContent =
            `Backend: ERROR - ${error.message}`;
    }
}


async function checkDatabase() {

    const dbElement = document.getElementById("db-status");

    try {

        const response =
            await fetch(`${BACKEND_URL}/db-test`);

        if (!response.ok) {
            throw new Error("Database request failed");
        }

        const data = await response.json();

        if (data.status === "connected") {

            dbElement.textContent =
                `Cloud SQL: Connected (${data.database})`;

        } else {

            dbElement.textContent =
                `Cloud SQL: Connection failed`;
        }

    } catch (error) {

        dbElement.textContent =
            `Cloud SQL: ERROR - ${error.message}`;
    }
}


async function checkConfiguration() {

    const configElement =
        document.getElementById("config-status");

    try {

        const response =
            await fetch(`${BACKEND_URL}/config-test`);

        const data = await response.json();

        if (
            data.db_name_configured &&
            data.db_user_configured &&
            data.db_password_configured &&
            data.cloud_sql_socket_configured
        ) {

            configElement.textContent =
                "Backend configuration: OK";

        } else {

            configElement.textContent =
                "Backend configuration: INCOMPLETE";
        }

    } catch (error) {

        configElement.textContent =
            "Backend configuration: ERROR";
    }
}


window.addEventListener("DOMContentLoaded", () => {

    checkBackend();
    checkDatabase();
    checkConfiguration();

});