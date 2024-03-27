import Home from "@/pages/Home.vue";
import {createRouter, createWebHistory} from "vue-router";
import tutorial from "@/pages/Tutorial.vue";
import Previewer from "@/pages/Previewer.vue";

const routes = [
    {
        path: "/",
        name: "Home",
        component: Home
    },
    {
        path: "/tutorial",
        name: "tutorial",
        component: tutorial
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