import Home from "@/pages/Home.vue";
import {createRouter, createWebHistory} from "vue-router";
import tutorial from "@/pages/Tutorial.vue";
import Previewer from "@/pages/Previewer.vue";
import AndroidPayTutorial from "@/pages/AndroidPayTutorial.vue";

const routes = [
    {
        path: "/",
        name: "Home",
        component: Home,
    },
    {
        path: "/tutorial/android/pay",
        name: "androidPayTutorial",
        component: AndroidPayTutorial
    },
    {
        path: "/preview/:pdfUrl",
        name: "preview",
        component: Previewer
    },
    {
        path: "/preview/:pdfUrl",
        name: "preview",
        component: Previewer
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
export default router