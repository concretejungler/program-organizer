// API Client for Program Organizer

const API = {
    async request(method, url, data = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (data) opts.body = JSON.stringify(data);

        const resp = await fetch(url, opts);
        const json = await resp.json();
        if (!resp.ok) throw new Error(json.error || 'Request failed');
        return json;
    },

    // Programs
    getPrograms(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.set('search', params.search);
        if (params.tag) query.set('tag', params.tag);
        if (params.sort) query.set('sort', params.sort);
        if (params.favorites) query.set('favorites', 'true');
        return this.request('GET', `/api/programs?${query}`);
    },

    getProgram(id) {
        return this.request('GET', `/api/programs/${id}`);
    },

    updateProgram(id, data) {
        return this.request('PUT', `/api/programs/${id}`, data);
    },

    deleteProgram(id) {
        return this.request('DELETE', `/api/programs/${id}`);
    },

    launchProgram(id) {
        return this.request('POST', `/api/programs/${id}/launch`);
    },

    stopProgram(id) {
        return this.request('POST', `/api/programs/${id}/stop`);
    },

    // Tags
    getTags() {
        return this.request('GET', '/api/tags');
    },

    createTag(name) {
        return this.request('POST', '/api/tags', { name });
    },

    deleteTag(id) {
        return this.request('DELETE', `/api/tags/${id}`);
    },

    // Settings
    getSettings() {
        return this.request('GET', '/api/settings');
    },

    updateSettings(data) {
        return this.request('PUT', '/api/settings', data);
    },

    // System
    scan() {
        return this.request('POST', '/api/scan');
    },

    getRuntimes() {
        return this.request('GET', '/api/runtimes');
    },
};
