import axios from 'axios';

// Axios client
const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
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

        scrapes: {
            get: async (webpage_id: number) => {
                const request = apiClient.get(`/webpages/${webpage_id}/scrapes`);
                return fetchData(request);
            },

            data: async (webpage_id: number) => {
                const request = apiClient.get(`/webpages/${webpage_id}/scrapes/data`);
                return fetchData(request);
            }
        }
    },

    scrapes: {
        get: async () => {
            const request = apiClient.get('/scrapes/');
            return fetchData(request);
        },

        runAll: async () => {
            const request = apiClient.post('/scrapes/run-all');
            return fetchData(request);
        },

        validate: async (data: any) => {
            const request = apiClient.post('/scrapes/validate', data);
            return fetchData(request);
        },

        create: async (webpage_id: number, data: any) => {
            const request = apiClient.post(`/scrapes/${webpage_id}`, data);
            return fetchData(request);
        },

        getById: async (scrape_id: number) => {
            const request = apiClient.get(`/scrapes/${scrape_id}`);
            return fetchData(request);
        },

        put: async (scrape_id: number, data: any) => {
            const request = apiClient.put(`/scrapes/${scrape_id}`, data);
            return fetchData(request);
        },

        patch: async (scrape_id: number, data: any) => {
            const request = apiClient.patch(`/scrapes/${scrape_id}`, data);
            return fetchData(request);
        },

        delete: async (scrape_id: number) => {
            const request = apiClient.delete(`/scrapes/${scrape_id}`);
            return fetchData(request);
        },

        data: async (scrape_id: number) => {
            const request = apiClient.get(`/scrapes/${scrape_id}/data`);
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
