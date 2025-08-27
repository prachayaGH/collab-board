import { createApp, watch } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';
import router from './router';
import { createPinia } from 'pinia'
import { useSocket } from "@/composables/useSocket";
import { useAuthStore } from "@/stores/auth";

const app = createApp(App);
app.use(createPinia())
app.use(PrimeVue);
app.use(router)

app.mount('#app')

// ✅ ใช้ authStore ตรวจ user
const authStore = useAuthStore();
const socket = useSocket();

// เฝ้าดูการเปลี่ยนแปลงของ user
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      console.log("🔌 User logged in → connect socket");
      socket.connect();
    } else {
      console.log("🔌 User logged out → disconnect socket");
      socket.disconnect();
    }
  },
  { immediate: true } // ตรวจสอบตั้งแต่แรก
);
