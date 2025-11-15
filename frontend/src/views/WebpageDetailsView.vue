
<template>
    <div class="webpage-details">
        <h1>Webpage details</h1>
        <div class="webpage-details-grid">
            <CardBasic
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
                                <th>Schedule time</th>
                                <td>{{ formatScheduleTime(webpage.run_time) }}</td>
                            </tr>
                            <tr>
                                <th>Schedule enabled</th>
                                <td>{{ webpage.is_enabled ? "Yes" : "No" }}</td>
                            </tr>
                            <!-- <tr>
                                <th>Webpage ID</th>
                                <td>{{ webpage.webpage_id }}</td>
                            </tr> -->
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
                        <button @click="runManualScrape" :disabled="loading.manualScrape" class="btn-with-icon">
                            <i class="bx bxs-right-arrow" :class="{'hidden': loading.manualScrape}"></i>
                            <span :class="{'hidden': loading.manualScrape}">Manual scrape</span>
                            <LoadingIndicator :hidden="!loading.manualScrape"/>
                        </button>
                    </div>
                </div>
            </CardBasic>
    
            <CardBasic
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
                        :label="element.metric_name"
                        :description="element.locator"
                        :actions="[
                            {
                                icon: 'bx bxs-edit',
                                method: editElement
                            },
                            {
                                icon: 'bx bxs-trash',
                                method: deleteElement
                            }
                        ]"
                    />
                </div>
                <ListingPlaceholder 
                    v-else
                    icon="bxs-layer"
                    text="No elements found"
                    desc="Create a new element using the form on the right."
                />
            </CardBasic>
    
            <CardBasic
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
            </CardBasic>

            <CardBasic
                icon="bxs-bar-chart-alt-2"
                class="g-d"
                title="Scraped data visualized" 
                description="View the scraped data in a graph"
            >
                <ChartLine
                    v-if="data.length > 0"
                    :chartData="data"
                />
                <ListingPlaceholder 
                    v-else
                    icon="bxs-bar-chart-alt-2"
                    text="No data found"
                    desc="The data scraped from the current webpage will be used to create a chart here."
                />
            </CardBasic>

            <CardBasic
                icon="bx bxs-file"
                class="g-e"
                title="Webpage logs"
                description="The logs for this webpages scrapes."
            >
                <div class="logs-wrapper">
                    <LogEntry 
                        v-for="(log, index) in logs"
                        :key="index"
                        :log="log"
                        :enableTopLevelLinks="false"
                    />
                </div>
                <ListingPlaceholder
                    v-if="logs.length === 0"
                    icon="bx bxs-file"
                    text="No logs found"
                    desc="Logs generated by scraping will appear here."
                />
            </CardBasic>
    
            <CardBasic
                class="g-f"
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
                            <td>{{ entry.metric_name }}</td>
                            <td>{{ entry.value }}</td>
                            <td>{{ formatTimestamp(entry.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
                <ListingPlaceholder 
                    v-else
                    icon="bxs-data"
                    text="No data found"
                    desc="The data scraped from the current webpage will appear here."
                />
            </CardBasic>
        </div>

        <ModalElement ref="modalElementRef"/>
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
        <ModalConfirmation 
            ref="modalDeleteElementConfirmationRef"
            title="Delete Element"
            description="Are you sure you want to delete the element? All of the gathered data will be removed permanently. This action is irreversible!"
            optionNegative="Back to safety"
            optionPositive="Delete permanently"
            :redHover="true"
        />
        <ModalConfirmation 
            ref="modalManualScrapeConfirmationRef"
            title="Run manual scrape"
            description="Note that scraping is intended to be automated. Run manually anyway?"
            optionPositive="Run scrape"
        />
    </div>
</template>

<script>
import CardBasic from '@/components/CardBasic.vue';
import ModalElement from '@/components/ModalElement.vue';
import ModalWebpage from '@/components/ModalWebpage.vue';
import ModalConfirmation from '@/components/ModalConfirmation.vue';
import FormElement from '@/components/FormElement.vue';
import InlineMessage from '@/components/InlineMessage.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import TextInput from '@/components/TextInput.vue';
import { fastApi } from '@/utils/fastApi';
import { formatTimestamp, formatScheduleTime } from '@/utils/utils';
import ChartLine from '@/components/ChartLine.vue';
import LogEntry from '@/components/LogEntry.vue';

export default {
    name: 'WebpageDetails',
    components: {
        CardBasic,
        ListEntry,
        LogEntry,
        LoadingIndicator,
        TextInput,
        InlineMessage,
        ListingPlaceholder,
        FormElement,
        ModalElement,
        ModalWebpage,
        ModalConfirmation,
        ChartLine,
    },
    data() {
        return {
            webpage: {},
            elements: [],
            data: [],
            logs: [],

            loading: {
                iframe: false,
                validate: false,
                elementCreate: false,
                manualScrape: false,
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
                // Attach metric_name to each data entry
                this.data = response.map(entry => {
                    const element = this.elements.find(el => el.element_id === entry.element_id);
                    return {
                        ...entry,
                        metric_name: element ? element.metric_name : ''
                    };
                }).sort((a, b) => a.data_id - b.data_id);
            }
        },
        async getWebpageLogs() {
            const resp = await fastApi.webpages.logs.get(this.$route.params.webpage_id);
            this.logs = resp || [];
        },
        formatTimestamp(time) {
            return formatTimestamp(time);
        },
        formatScheduleTime(time) {
            return formatScheduleTime(time);
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
            if (await this.$refs.modalDeleteElementConfirmationRef.open()) {
                const response = await fastApi.elements.delete(element.element_id);
                if (response) {
                    await this.getWebpageElements();
                    await this.getWebpageElementData();
                }
            }
        },
        
        ////////////// Webpage modification //////////////
        async deleteWebpage() {
            if (await this.$refs.modalDeleteWebpageConfirmationRef.open()) {
                const response = await fastApi.webpages.delete(this.webpage.webpage_id);
                if (response) {
                    this.$router.push("/webpages");
                }
            }
        },
        async editWebpage() {
            const response = await this.$refs.modalWebpageRef.open(this.webpage);
            if (response && response.success) {
                await this.getWebpageInfo();
            } 
            // Else we aborted returning success = false
        },

        async runManualScrape() {
            if (await this.$refs.modalManualScrapeConfirmationRef.open()) {
                this.loading.manualScrape = true;
                const response = await fastApi.webpages.runScrape(this.webpage.webpage_id);
                if (response) {
                    await this.getWebpageElementData();
                }
                this.loading.manualScrape = false;
            }
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
        await this.getWebpageLogs();
    },
}
</script>

<style scoped>
.webpage-details-grid {
    display: grid;
    gap: 16px;
    grid-template-columns: 4fr 4fr;
    grid-template-areas:
        "a a"
        "b c"
        "d d"
        "e e"
        "f f";
}
@media (max-width: 1000px) {
    .webpage-details-grid {
        grid-template-columns: 1fr;
            grid-template-areas:
            "a"
            "b"
            "c"
            "d"
            "e"
            "f";
    }
}

.logs-wrapper {
    display: flex;
    flex-direction: column;
    padding: 4px;
    gap: 8px;
    height: fit-content;
    max-height: min(50vh, 1000px);
    overflow: scroll;
}
</style>