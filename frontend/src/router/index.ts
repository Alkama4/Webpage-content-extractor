import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/', 
            redirect: '/webpages'
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
            {
            path: '/logs', 
            name: 'Logs',
            component: () => import('@/views/LogsView.vue')
        },
    ],
})

export default router
