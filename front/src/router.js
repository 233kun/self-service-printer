import Home from "@/pages/Home.vue";
import {createRouter, createWebHistory} from "vue-router";
import test from "@/pages/test.vue";

const routes = [
    {
            path: "/",
            name: "Home",
            component: Home
        },
        {
            path: "/test",
            name: "test",
            component: test
        }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
export default router