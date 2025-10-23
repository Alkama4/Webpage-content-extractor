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
                <div class="flex-col gap-16">
                    <table>
                        <tbody>
                            <tr>
                                <th>Metric name</th>
                                <td>{{ element.metric_name }}</td>
                            </tr>
                            <tr>
                                <th>Locator string</th>
                                <td>{{ element.locator }}</td>
                            </tr>
                            <tr>
                                <th>Element ID</th>
                                <td>{{ element.element_id }}</td>
                            </tr>
                            <tr>
                                <th>Parent webpage</th>
                                <td>{{ parentWebpage.page_name }} (ID {{ parentWebpage.webpage_id }})</td>
                            </tr>
                            <tr>
                                <th>Data count</th>
                                <td>{{ dataCount }} datapoint{{ dataCount == 1 ? '' : 's' }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="flex-row gap-8">
                        <button @click="editElement" class="btn-with-icon">
                            <i class="bx bxs-edit"></i>
                            <span>Edit</span>
                        </button>
                        <button @click="deleteElement" class="btn-with-icon btn-danger">
                            <i class="bx bxs-trash"></i>
                            <span>Delete</span>
                        </button>
                    </div>
                </div>
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
                            <td>{{ formatTimestamp(entry.created_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </BasicCard>
        </div>

        <ModalElement ref="modalElementRef"/>
        <ModalConfirmation 
            ref="modalDeleteElementConfirmationRef"
            title="Delete Element"
            description="Are you sure you want to delete the element? All of the gathered data will be removed permanently. This action is irreversible!"
            optionNegative="Back to safety"
            optionPositive="Delete permanently"
            :redHover="true"
        />
    </div>
</template>

<script>
import BasicCard from '@/components/CardBasic.vue';
import FormElement from '@/components/FormElement.vue';
import ModalElement from '@/components/ModalElement.vue'
import ModalConfirmation from '@/components/ModalConfirmation.vue'
import { fastApi } from '@/utils/fastApi';
import { formatTimestamp } from '@/utils/utils';

export default {
    name: 'ElementDetails',
    components: {
        BasicCard,
        FormElement,
        ModalElement,
        ModalConfirmation,
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
        formatTimestamp(time) {
            return formatTimestamp(time);
        },

        async editElement() {
            const response = await this.$refs.modalElementRef.open(this.parentWebpage.url, this.parentWebpage.webpage_id, this.element);
            if (response && response.success) {
                await this.getElementInfo();
            } 
        },
        async deleteElement() {
            if (await this.$refs.modalDeleteElementConfirmationRef.open()) {
                const response = await fastApi.elements.delete(this.element.element_id);
                if (response) {
                    this.$router.push(`/webpages/${this.parentWebpage.webpage_id}`);
                }
            }
        },
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