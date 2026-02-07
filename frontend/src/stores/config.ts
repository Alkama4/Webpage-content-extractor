import { defineStore } from 'pinia';
import { fastApi } from '../utils/fastApi';

interface ConfigResponse {
    read_only_mode: boolean;
}

export const useConfigStore = defineStore('config', {
    state: () => ({
        read_only_mode: false as boolean,
    }),
    actions: {
        async fetchConfig() {
            const response = await fastApi.config.get() as ConfigResponse;
            this.read_only_mode = response?.read_only_mode ?? false; 
        }
    }
});