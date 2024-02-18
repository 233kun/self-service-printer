import './assets/main.css'
import "element-plus/dist/index.css"
import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router.js";
import naive from "naive-ui";
import elementPlus from "element-plus"

const app = createApp(App)
app.use(router)
app.use(naive)
app.use(elementPlus)
app.mount('#app')

