<template>
    <div class="form-schedule flex-col gap-8">
        <InlineMessage 
            :text="requestErrorMsg" 
            :interaction="true"
            @close="requestErrorMsg = ''"
            v-if="requestErrorMsg"
        />
        <form @submit.prevent="webpageCreateOrUpdate">
            <TimeInput
                v-model="newWebpageDetails.run_time"
                label="Scheduled scrape time"
            />

            <button type="submit" :disabled="loading.formSubmit">
                <LoadingIndicator :hidden="!loading.formSubmit"/>
                <span :class="{'hidden': loading.formSubmit}">
                    Update webpage
                </span>
            </button>
        </form>
    </div>
</template>

<script>
import InlineMessage from './InlineMessage.vue';
import LoadingIndicator from './LoadingIndicator.vue';
import TextInput from './TextInput.vue';
import TimeInput from './TimeInput.vue';
import { fastApi } from '@/utils/fastApi';

export default {
    name: 'FormSchedule',
    data() {
        return {
            loading: {
                formSubmit: false,
            },
            requestErrorMsg: '',

            // Iframe stuff
            previewHtml: '',
            locatorMatchCount: 0,
            selectedWebpage: null,
            newWebpageDetails: {
                url: '',
                page_name: ''
            }
        }
    },
    components: {
        TextInput,
        TimeInput,
        LoadingIndicator,
        InlineMessage,
    },
    emits: ['success'],
    props: {
        existingWebpage: {
            type: Object,
            default: null
        }
    },
    methods: {
        async webpageCreateOrUpdate() {
            this.loading.formSubmit = true;
            try {
                const response = this.existingWebpage
                    ? await fastApi.webpages.patch(this.existingWebpage.webpage_id, this.newWebpageDetails)
                    : await fastApi.webpages.post(this.newWebpageDetails);
                if (response) {
                    this.$emit('success')
                    // Wipe errors
                    this.requestErrorMsg = '';
                }
            } catch(e) {
                this.requestErrorMsg = e.response?.data?.detail?.[0]?.msg 
                    ?? e.response?.data?.detail?.detail 
                    ?? e.message
                    ?? e
            } finally {
                this.loading.formSubmit = false
            }
        },
    },
    mounted() {
        if (this.existingWebpage) {
            this.newWebpageDetails = {
                run_time: this.existingWebpage.run_time || '',
            }
        }
    },
}
</script>
