<template>
    <div class="webpages-view">
        <h1>Webpages</h1>
        <div class="webpages-view-grid">
            <CardBasic
                icon="bx-list-ul"
                class=""
                title="Webpages" 
                description="Manage pages from which you scrape content"
            >
                <div class="vertical-scroll-list" v-if="webpages.length > 0">
                    <ListEntry
                        v-for="webpage in webpages"
                        :key="webpage.webpage_id"
                        :item="webpage"
                        :to="`/webpages/${webpage.webpage_id}`"
                        icon="bx bx-globe"
                        :label="webpage.page_name"
                        :description="webpage.url"
                        :actions="[
                            {
                                icon: 'bx bxs-edit',
                                method: editWebpage
                            },
                            {
                                icon: 'bx bxs-trash',
                                method: deleteWebpage
                            }
                        ]"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bx-globe"
                    text="No webpages found"
                    desc="Create a new webpage using the form on the right."
                />
            </CardBasic>

            <CardBasic
                icon="bx-list-plus"
                class=""
                title="Create a webpage" 
                description="Set up a new page for data extraction"
            >
                <FormWebpage @success="fetchWebpages"/>
            </CardBasic>
        </div>

        <ModalWebpage ref="modalWebpageRef"/>
        <ModalConfirmation 
            ref="modalDeleteWebpageConfirmationRef"
            title="Delete Webpage"
            description="Are you sure you want to delete the webpage? All of the elements and gathered data will be removed permanently. This action is irreversible!"
            optionNegative="Back to safety"
            optionPositive="Delete permanently"
            confirmationText="I am certain I wish to delete the webpage and all of its related data permanently."
            :redHover="true"
        />
    </div>
</template>

<script>
import CardBasic from '@/components/CardBasic.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import TextInput from '@/components/TextInput.vue'
import { fastApi } from '@/utils/fastApi';
import FormWebpage from '@/components/FormWebpage.vue'
import ModalWebpage from '@/components/ModalWebpage.vue'
import ModalConfirmation from '@/components/ModalConfirmation.vue'
import { useConfigStore } from '@/stores/config';

export default {
    name: 'App',
    components: {
        CardBasic,
        ListingPlaceholder,
        TextInput,
        ListEntry,
        FormWebpage,
        ModalWebpage,
        ModalConfirmation,
    },
    data() {
        return {
            webpages: []
        };
    },
    methods: {
        async deleteWebpage(webpage) {
            if (await this.$refs.modalDeleteWebpageConfirmationRef.open()) {
                try {
                    const response = await fastApi.webpages.delete(webpage.webpage_id);
                    if (response) {
                        await this.fetchWebpages();
                    }
                } catch {
                    const configStore = useConfigStore();
                    this.$notify(`Failed to delete webpage: ${configStore.read_only_mode ? 'Read-only mode' : 'Unknown error'}`);
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
    /* max-width: 1200px; */
    margin: 0 auto;
}

.webpages-view-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--card-gap);
}
@media(max-width: 1000px) {
    .webpages-view-grid {
        grid-template-columns: 1fr;
    }
}
</style>
