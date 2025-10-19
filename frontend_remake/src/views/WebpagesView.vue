<template>
    <div class="webpages-view">
        <h1>Webpages</h1>
        <div class="webpages-view-grid gap-16">
            <BasicCard
                icon="bx-list-ul"
                class=""
                title="Webpages" 
                description="Manage pages from which you scrape content"
            >
                <div class="entry-list-wrapper" v-if="webpages.length > 0">
                    <ListEntry
                        v-for="webpage in webpages"
                        :key="webpage.webpage_id"
                        :item="webpage"
                        :to="`/webpages/${webpage.webpage_id}`"
                        icon="bx bx-globe"
                        labelField="page_name"
                        subField="url"
                        :onEdit="editWebpage"
                        :onDelete="deleteWebpage"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-globe"
                    text="No webpages found"
                    desc="Create a new webpage using the form on the right."
                />
            </BasicCard>

            <BasicCard
                icon="bx-list-plus"
                class=""
                title="Create a webpage" 
                description="Set up a new page for data extraction"
            >
                <FormWebpage @success="fetchWebpages"/>
            </BasicCard>
        </div>

        <ModalWebpage ref="modalWebpageRef"/>
    </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import TextInput from '@/components/TextInput.vue'
import { fastApi } from '@/utils/fastApi';
import FormWebpage from '@/components/FormWebpage.vue'
import ModalWebpage from '@/components/ModalWebpage.vue'

export default {
    name: 'App',
    components: {
        BasicCard,
        ListingPlaceholder,
        TextInput,
        ListEntry,
        FormWebpage,
        ModalWebpage,
    },
    data() {
        return {
            webpages: []
        };
    },
    methods: {
        async deleteWebpage(webpage) {
            if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
                const response = await fastApi.webpages.delete(webpage.webpage_id);
                if (response) {
                    await this.fetchWebpages();
                }
            }
        },

        async editWebpage(webpage) {
            const response = await this.$refs.modalWebpageRef.open(webpage);
            if (response && response.success) {
                await this.fetchWebpages();
            } 
            // Else we aborted returning success = false
        },

        async fetchWebpages() {
            const response = await fastApi.webpages.get()
            if (response) {
                this.webpages = response;
            }
        },
    },

    async mounted() {
        await this.fetchWebpages()
    },
};
</script>

<style scoped>
.webpages-view {
    max-width: 1200px;
    margin: 0 auto;
}

.webpages-view h1 {
    font-size: var(--fs-8);
    font-weight: var(--fw-bold);
    color: var(--text-dark-primary);
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.webpages-view-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    margin-top: 2rem;
}
@media(max-width: 1000px) {
    .webpages-view-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}
</style>
