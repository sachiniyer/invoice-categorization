export const register_user = async (username: string, password: string, url: string) => {
    const response = await fetch(url, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password })
    });
    if (response.status !== 200) {
        throw new Error("api failed");
    }
    return await response.json();
}

export const login_user = async (username: string, password: string, url: string) => {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },

        body: JSON.stringify({ username, password })
    });
    if (response.status !== 200) {
        throw new Error("api failed");
    }
    return await response.json();
}

export const verify_token = async (token: string, url: string) => {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ token })
    });
    if (response.status !== 200) {
        throw new Error("api failed");
    }
    return await response.json();
}

export const update_password = async (username: string, password: string, token: string, url: string) => {
    const response = await fetch(url, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password, token })
    });
    if (response.status !== 200) {
        throw new Error("api failed");
    }
    return await response.json();
}

export const delete_user = async (username: string, token: string, url: string) => {
    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, token })
    });
    if (response.status !== 200) {
        throw new Error("api failed");
    }
    return await response.json();
}
