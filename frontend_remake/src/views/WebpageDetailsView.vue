<template>
    <div class="webpage-details">
        <h1>Webpage details</h1>
        <div class="webpage-details-grid">
            <BasicCard
                class="g-a"
                icon="bxs-info-circle"
                title="Webpage info"
                description="Inspect the details of a webpage"
            >
                <div class="flex-col gap-16">
                    <table>
                        <tbody>
                            <tr>
                                <th>Name</th>
                                <td>{{ webpage.page_name }}</td>
                            </tr>
                            <tr>
                                <th>URL</th>
                                <td><a :href="webpage.url">{{ webpage.url }}</a></td>
                            </tr>
                            <tr>
                                <th>Element count</th>
                                <td>{{ elementCount }} element{{ elementCount == 1 ? '' : 's' }}</td>
                            </tr>
                            <tr>
                                <th>Data count</th>
                                <td>{{ dataCount }} datapoint{{ dataCount == 1 ? '' : 's' }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="flex-row gap-8">
                        <button @click="editWebpage" class="btn-with-icon">
                            <i class="bx bxs-edit"></i>
                            <span>Edit</span>
                        </button>
                        <button @click="deleteWebpage" class="btn-with-icon btn-danger">
                            <i class="bx bxs-trash"></i>
                            <span>Delete</span>
                        </button>
                    </div>
                </div>
            </BasicCard>
    
            <BasicCard
                class="g-b"
                style="min-width: 500px;"
                icon="bx-list-ul"
                title="Webpage elements"
                description="Elements that are scraped from the webpage"
            >
                <div v-if="elements?.length > 0" class="entry-list-wrapper">
                    <ListEntry
                        v-for="element in elements"
                        :key="element.element_id"
                        :item="element"
                        :to="`/webpages/${webpage.webpage_id}/elements/${element.element_id}`"
                        icon="bx bxs-layer"
                        labelField="metric_name"
                        subField="locator"
                        :onEdit="editElement"
                        :onDelete="deleteElement"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bxs-layer"
                    text="No elements found"
                    desc="Create a new element using the form on the right."
                />
            </BasicCard>
    
            <BasicCard
                class="g-c"
                icon="bx-list-plus"
                title="Create a new element"
                description="Set up a new element to be scraped from the page"
            >
                <FormElement
                    :webpageUrl="webpage.url"
                    :webpageId="webpage.webpage_id"
                    @success="getWebpageElements"
                />
            </BasicCard>
    
            <BasicCard
                class="g-d"
                icon="bxs-data"
                title="Scraped webpage data"
                description="Inspect the data that has been scraped from the current webpage"
            >
                <table v-if="data?.length > 0">
                    <tbody>
                        <tr>
                            <th>Data ID</th>
                            <th>Element ID</th>
                            <th>Metric</th>
                            <th>Value</th>
                            <th>Timestamp</th>
                        </tr>
                        <tr v-for="entry in data">
                            <td>{{ entry.data_id }}</td>
                            <td>{{ entry.element_id }}</td>
                            <td>{{ findMetricName(entry.element_id) }}</td>
                            <td>{{ entry.value }}</td>
                            <td>{{ formatTime(entry.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
                <ListingPlaceholder 
                    v-else
                    icon="bxs-data"
                    text="No data found"
                    desc="The data scraped from the current webpage will appear here."
                />
            </BasicCard>
        </div>

        <ModalElement ref="modalElementRef"/>
    </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import ModalElement from '@/components/ModalElement.vue';
import FormElement from '@/components/FormElement.vue';
import InlineMessage from '@/components/InlineMessage.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import TextInput from '@/components/TextInput.vue';
import { fastApi } from '@/utils/fastApi';
import { formatTime } from '@/utils/utils';

export default {
    name: 'WebpageDetails',
    components: {
        BasicCard,
        ListEntry,
        LoadingIndicator,
        TextInput,
        InlineMessage,
        ListingPlaceholder,
        FormElement,
        ModalElement,
    },
    data() {
        return {
            webpage: {},
            elements: [],
            data: [],

            loading: {
                iframe: false,
                validate: false,
                elementCreate: false,
            },
            failed: {
                valueParse: false,
                emptyFields: false,
                alreadyExists: false,
            },

            // Iframe stuff
            iframeLoaded: false,
            previewHtml: '',
            validationResult: null,
            locatorMatchCount: 0,
            displayeElementDetails: {
                element: null,
                locator: ''
            },
            newElemenDetails: {
                locator: '',
                metric_name: ''
            }
        }
    },
    methods: {
        async getWebpageInfo() {
            const response = await fastApi.webpages.getById(this.$route.params.webpage_id);
            if (response) {
                this.webpage = response;
            }
        },
        async getWebpageElements() {
            const response = await fastApi.webpages.elements.get(this.$route.params.webpage_id);
            if (response) {
                this.elements = response.sort((a, b) => a.element_id - b.element_id);
            }
        },
        async getWebpageElementData() {
            const response = await fastApi.webpages.elements.data(this.$route.params.webpage_id);
            if (response) {
                this.data = response.sort((a, b) => a.data_id - b.data_id);
            }
        },
        formatTime(time) {
            return formatTime(time);
        },
        findMetricName(elementId) {
            const element = this.elements.find(s => s.element_id === elementId);
            return element ? element.metric_name : '';
        },
        async editElement(element) {
            const response = await this.$refs.modalElementRef.open(this.webpage.url, this.webpage.webpage_id, element);
            if (response && response.success) {
                await this.getWebpageElements();
            } 
            // Else we aborted returning success = false
        },
        async deleteElement(element) {
            if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
                const response = await fastApi.elements.delete(element.element_id);
                if (response) {
                    await this.getWebpageElements();
                    await this.getWebpageElementData();
                }
            }
        },
        
        ////////////// Webpage modification //////////////
        async deleteWebpage() {
            if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
                const response = await fastApi.webpages.delete(this.webpage.webpage_id);
                if (response) {
                    this.$router.push("/webpages");
                }
            }
        },
        editWebpage() {
            alert("TBD");
        },
    },
    computed: {
        elementCount() {
            return this.elements.length;
        },
        dataCount() {
            return this.data.length;
        },
    },
    async mounted() {
        await this.getWebpageInfo();
        await this.getWebpageElements();
        await this.getWebpageElementData();
    },
}
</script>

<style scoped>
.webpage-details-grid {
    display: grid;
    gap: 16px;
    grid-template-columns: 4fr 3fr;
    grid-template-areas:
        "a a"
        "b c"
        "d d";
}
@media (max-width: 1000px) {
    .webpage-details-grid {
        grid-template-columns: 1fr;
            grid-template-areas:
            "a"
            "b"
            "c"
            "d";
    }
}
</style>