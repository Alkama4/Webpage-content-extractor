import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/', 
            component: () => import('@/views/HomeView.vue')
        },
        {
            path: '/webpages', 
            component: () => import('@/views/WebpagesView.vue')
        },
        {
            path: '/webpages/:webpage_id',
            component: () => import('@/views/WebpageDetailsView.vue')
        },
        {
            path: '/elements/:element_id',
            component: () => import('@/views/ElementDetailsView.vue')
        }
    ],
})

export default router
