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
            name: 'Webpages',
            component: () => import('@/views/WebpagesView.vue')
        },
        {
            path: '/webpages/:webpage_id',
            name: 'Webpage details',
            component: () => import('@/views/WebpageDetailsView.vue')
        },
        {
            path: '/webpages/:webpage_id/elements/:element_id',
            name: 'Element details',
            component: () => import('@/views/ElementDetailsView.vue'),
        },
        {
            path: '/data', 
            name: 'Data',
            component: () => import('@/views/DataView.vue')
        },
        {
            path: '/scheduler', 
            name: 'Scheduler',
            component: () => import('@/views/SchedulerView.vue')
        },
    ],
})

export default router
