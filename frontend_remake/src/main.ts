import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@/assets/global.css'
import '@/assets/variables.css'
import '@/assets/fonts.css'
import '@/assets/utils.css'
import 'boxicons/css/boxicons.min.css';

const app = createApp(App)

app.use(router)

app.mount('#app')
