import {createRouter, createWebHistory} from "vue-router";
import AndroidPayTutorial from "@/pages/AndroidPayTutorial.vue";
const routes = [
    {
        path: "/",
        name: "Home",
        component: () => import ("@/pages/Home.vue"),
        meta: {
            title: "自助打印",
        }
    },
    {
        path: "/tutorial/android/pay",
        name: "androidPayTutorial",
        component: AndroidPayTutorial
    }
    // legacy page
    // using '/pdfjs/web/viewer.html?file=' instead
    // {
    //     path: "/preview/:pdfUrl",
    //     name: "preview",
    //     component: Previewer
    // },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
router.beforeEach((to, from, next) => {
  document.title = to.meta.title;
  next();
})
export default router