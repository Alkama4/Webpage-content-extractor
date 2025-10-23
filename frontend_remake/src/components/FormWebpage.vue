<template>
    <div class="form-webpage flex-col gap-8">
        <InlineMessage 
            :text="requestErrorMsg" 
            :interaction="true"
            @close="requestErrorMsg = ''"
            v-if="requestErrorMsg"
        />
        <form @submit.prevent="webpageCreateOrUpdate">
            <TextInput
                v-model="newWebpageDetails.page_name"
                label="Page name"
                placeholder="The webpages name"
            />
            <TextInput
                v-model="newWebpageDetails.url"
                label="URL"
                placeholder="http://example.com"
            />
            <TimeInput
                v-model="newWebpageDetails.run_time"
                label="Scheduled scrape time"
            />
            <ToggleInput
                v-model="newWebpageDetails.is_enabled"
                label="Scraping enabled"
            />
            <button type="submit">
                <LoadingIndicator v-if="loading.formSubmit"/>
                <span v-else>{{ existingWebpage ? 'Update webpage' : 'Create webpage' }}</span>
            </button>
        </form>
    </div>
</template>

<script>
import InlineMessage from './InlineMessage.vue';
import LoadingIndicator from './LoadingIndicator.vue';
import TextInput from './TextInput.vue';
import TimeInput from './TimeInput.vue';
import ToggleInput from './ToggleInput.vue';
import { fastApi } from '@/utils/fastApi';
import { toInputTime } from '@/utils/utils';

export default {
    name: 'FormWebpage',
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
        ToggleInput,
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
                    ? await fastApi.webpages.put(this.existingWebpage.webpage_id, this.newWebpageDetails)
                    : await fastApi.webpages.post(this.newWebpageDetails);
                if (response) {
                    this.$emit('success')
                    if (!this.existingWebpage) {
                        this.newWebpageDetails = { url: '', page_name: '' };
                    }
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
            console.log(this.existingWebpage)
            this.newWebpageDetails = {
                url: this.existingWebpage.url || '',
                page_name: this.existingWebpage.page_name || '',
                run_time: toInputTime(this.existingWebpage.run_time) || '',
                is_enabled: this.existingWebpage.is_enabled || false
            }
            console.log(this.newWebpageDetails)
        }
    },
}
</script>
