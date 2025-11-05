<template>
    <div class="data-view">
        <h1>Data analysis</h1>

        <!-- A card for each webpage -->
        <CardBasic
            v-for="webpage in webpages"
            :key="webpage.webpage_id"
            icon="bx bx-globe"
            class="card-wrapper"
            :title="webpage.page_name"
            description="Scraped data visualized"
            :link="`/webpages/${webpage.webpage_id}`"
        >
            <!-- Pass the enriched array to ChartLine -->
            <ChartLine
                v-if="pageData[webpage.webpage_id]?.length > 0"
                :chartData="pageData[webpage.webpage_id]"
            />
            <ListingPlaceholder
                v-else
                icon="bx-globe"
                text="No data found"
                desc="The data scraped from this webpage will be used to create a chart here."
            />
        </CardBasic>

        <!-- If there are no webpages at all, show one global placeholder -->
        <ListingPlaceholder
            v-if="webpages.length === 0"
            icon="bx bx-globe"
            text="No webpages found"
            desc="Create a new webpage to start collecting data."
        />
    </div>
</template>

<script>
import { fastApi } from '@/utils/fastApi';
import CardBasic from '@/components/CardBasic.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import ChartLine from '@/components/ChartLine.vue';

export default {
    name: 'DataView',
    components: { CardBasic, ListingPlaceholder, ChartLine },

    data() {
        return {
            webpages: [],   // list of webpages
            pageData: {}    // map of webpage_id → array of enriched datapoints
        };
    },

    methods: {
        /* Fetch all webpages */
        async fetchWebpages() {
            const resp = await fastApi.webpages.get();
            this.webpages = resp || [];

            // initialise empty array for each page
            this.webpages.forEach(wp => {
                this.pageData[wp.webpage_id] = [];
            });
        },

        /* Fetch data for a single page */
        async fetchDataForPage(webpage_id) {
            const resp = await fastApi.webpages.elements.data(webpage_id);
            return resp || [];
        },

        /* Load data for every page in parallel and enrich it with metric_name */
        async loadAllPageData() {
            // first cache elements per page (needed to get metric names)
            this.elementsCache = {};
            const elementPromises = this.webpages.map(async wp => {
                const elems = await fastApi.webpages.elements.get(wp.webpage_id);
                this.elementsCache[wp.webpage_id] = elems || [];
            });
            await Promise.all(elementPromises);

            // now fetch data and enrich
            const promises = this.webpages.map(async wp => {
                const rawData = await this.fetchDataForPage(wp.webpage_id);
                const enriched = rawData.map(entry => ({
                    ...entry,
                    metric_name: this.findMetricName(entry.element_id, wp.webpage_id)
                }));
                this.pageData[wp.webpage_id] = enriched;
            });
            await Promise.all(promises);
        },

        /* Find metric name for an element within a page */
        findMetricName(element_id, webpage_id) {
            const elements = this.elementsCache[webpage_id] || [];
            const el = elements.find(e => e.element_id === element_id);
            return el ? el.metric_name : '';
        }
    },

    async mounted() {
        await this.fetchWebpages();
        await this.loadAllPageData();
    },

    /* non‑reactive cache */
    elementsCache: {}
};
</script>

<style scoped>
.data-view {
    /* max-width: 1200px; */
    margin: 0 auto;
}
.card-wrapper + .card-wrapper {
    margin-top: 1.5rem;
}
</style>
