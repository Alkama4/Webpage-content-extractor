import axios from 'axios';

// Axios client
const apiClient = axios.create({
    baseURL: import.meta.env.DEV ? 'http://localhost:8000' : '/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Helper to log full response and return only data
async function fetchData<T>(request: Promise<any>): Promise<T> {
    try {
        const response = await request;
        const method = response.config?.method?.toUpperCase();
        const url = response.config?.url;
        console.debug(`${method} ${url}`, response);
        return response.data;
    } catch (error: any) {
        console.error('API error:', error);
        throw error;
    }
}

export const fastApi = {
    root: {
        get: async () => {
            const request = apiClient.get('/');
            return fetchData(request);
        }
    },

    webpages: {
        get: async (params?: Record<string, any>) => {
            const request = apiClient.get('/webpages/', { params });
            return fetchData(request);
        },

        post: async (data: any) => {
            const request = apiClient.post('/webpages/', data);
            return fetchData(request);
        },

        getById: async (webpage_id: number) => {
            const request = apiClient.get(`/webpages/${webpage_id}`);
            return fetchData(request);
        },

        put: async (webpage_id: number, data: any) => {
            const request = apiClient.put(`/webpages/${webpage_id}`, data);
            return fetchData(request);
        },

        patch: async (webpage_id: number, data: any) => {
            const request = apiClient.patch(`/webpages/${webpage_id}`, data);
            return fetchData(request);
        },

        delete: async (webpage_id: number) => {
            const request = apiClient.delete(`/webpages/${webpage_id}`);
            return fetchData(request);
        },

        elements: {
            get: async (webpage_id: number) => {
                const request = apiClient.get(`/webpages/${webpage_id}/elements`);
                return fetchData(request);
            },

            data: async (webpage_id: number) => {
                const request = apiClient.get(`/webpages/${webpage_id}/elements/data`);
                return fetchData(request);
            }
        }
    },

    elements: {
        get: async () => {
            const request = apiClient.get('/elements/');
            return fetchData(request);
        },

        runAll: async () => {
            const request = apiClient.post('/elements/run-all');
            return fetchData(request);
        },

        validate: async (data: any) => {
            const request = apiClient.post('/elements/validate', data);
            return fetchData(request);
        },

        create: async (webpage_id: number, data: any) => {
            const request = apiClient.post(`/elements/${webpage_id}`, data);
            return fetchData(request);
        },

        getById: async (element_id: number) => {
            const request = apiClient.get(`/elements/${element_id}`);
            return fetchData(request);
        },

        put: async (element_id: number, data: any) => {
            const request = apiClient.put(`/elements/${element_id}`, data);
            return fetchData(request);
        },

        patch: async (element_id: number, data: any) => {
            const request = apiClient.patch(`/elements/${element_id}`, data);
            return fetchData(request);
        },

        delete: async (element_id: number) => {
            const request = apiClient.delete(`/elements/${element_id}`);
            return fetchData(request);
        },

        data: async (element_id: number) => {
            const request = apiClient.get(`/elements/${element_id}/data`);
            return fetchData(request);
        }
    },

    preview: {
        get: async (params: { url: string }) => {
            const request = apiClient.get('/preview', { params });
            return fetchData(request);
        }
    }
};
