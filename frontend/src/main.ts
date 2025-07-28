import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';
import router from './router';
import { createPinia } from 'pinia'

const app = createApp(App);
app.use(createPinia())
app.use(PrimeVue);
app.use(router)
app.mount('#app');
