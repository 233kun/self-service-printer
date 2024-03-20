import Home from "@/pages/Home.vue";
import {createRouter, createWebHistory} from "vue-router";
import tutorial from "@/pages/tutorial.vue";

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
        }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
export default router