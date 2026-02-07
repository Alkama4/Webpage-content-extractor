import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import '@/assets/global.css'
import '@/assets/variables.css'
import '@/assets/fonts.css'
import '@/assets/utils.css'
import 'boxicons/css/boxicons.min.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.config.globalProperties.$notify = (msg: string) => {
    window.dispatchEvent(new CustomEvent('notify', { detail: msg }));
};

app.mount('#app')
