<template>
    <div class="element-details-view">
        <h1>Element details</h1>
        <div class="flex-col gap-16">
            <BasicCard
                class="g-a"
                icon="bxs-info-circle"
                title="Element info"
                description="Inspect the details of the element"
            >
                <table>
                    <tbody>
                        <tr>
                            <th>Metric name</th>
                            <td>{{ element.metric_name }}</td>
                        </tr>
                        <tr>
                            <th>Parent webpage</th>
                            <td>{{ parentWebpage.page_name }} (ID {{ parentWebpage.webpage_id }})</td>
                        </tr>
                        <tr>
                            <th>Locator string</th>
                            <td>{{ element.locator }}</td>
                        </tr>
                        <tr>
                            <th>Data count</th>
                            <td>{{ dataCount }} datapoint{{ dataCount == 1 ? '' : 's' }}</td>
                        </tr>
                    </tbody>
                </table>
            </BasicCard>

            <BasicCard
                class="g-c"
                icon="bx-list-plus"
                title="Edit element details"
                description="View the selected element in the preview and click it to generate a new selector, or manually edit its locator string or metric name."
            >
                <FormElement
                    :webpageUrl="parentWebpage.url"
                    :webpageId="parentWebpage.webpage_id"
                    :existingElement="element"
                    @success="getElementInfo"
                />
            </BasicCard>
    
            <BasicCard
                class="g-d"
                icon="bxs-data"
                title="Scraped element data"
                description="Inspect the data that has been scraped from the element"
            >
                <table>
                    <tbody>
                        <tr>
                            <th>Data ID</th>
                            <th>Element ID</th>
                            <th>Value</th>
                            <th>Timestamp</th>
                        </tr>
                        <tr v-for="entry in data">
                            <td>{{ entry.data_id }}</td>
                            <td>{{ entry.element_id }}</td>
                            <td>{{ entry.value }}</td>
                            <td>{{ formatTime(entry.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </BasicCard>
        </div>
    </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import FormElement from '@/components/FormElement.vue';
import { fastApi } from '@/utils/fastApi';
import { formatTime } from '@/utils/utils';

export default {
    name: 'ElementDetails',
    components: {
        BasicCard,
        FormElement,
    },
    data() {
        return {
            element: {},
            parentWebpage: {},
            data: [],
        }
    },
    methods: {
        async getElementInfo() {
            const response = await fastApi.elements.getById(this.$route.params.element_id);
            if (response) {
                this.element = response;
            }
        },
        async getElementData() {
            const response = await fastApi.elements.data(this.$route.params.element_id);
            if (response) {
                this.data = response;
            }
        },
        async getParentWebpageInfo() {
            const response = await fastApi.webpages.getById(this.$route.params.webpage_id);
            if (response) {
                this.parentWebpage = response;
            }
        },
        formatTime(time) {
            return formatTime(time);
        }
    },
    computed: {
        dataCount() {
            return this.data?.length || 0;
        }
    },
    async mounted() {
        await this.getElementInfo();
        await this.getParentWebpageInfo();
        await this.getElementData();
    }
}
</script>