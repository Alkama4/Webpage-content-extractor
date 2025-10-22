<template>
    <ModalBasic 
        ref="modalBasic"
        :title="existingElement ? 'Edit element' : 'Create element'"
        :description="existingElement 
            ? 'Modify an existing elements metric name or locator string.' 
            : 'Set up a new element to be scraped from the page'"
        :icon="existingElement ? 'bxs-edit' : 'bx-list-plus'"
        @closed="handleClosed"
    >
        <FormElement
            :webpageUrl="webpageUrl"
            :webpageId="webpageId"
            :existingElement="existingElement"
            @success="handleSuccess"
        />
    </ModalBasic>
</template>

<script>
import ModalBasic from '@/components/ModalBasic.vue'
import FormElement from '@/components/FormElement.vue'

export default {
    name: 'ModalElement',
    components: { ModalBasic, FormElement },

    data() {
        return {
            visible: false,
            webpageUrl: '',
            webpageId: null,
            existingElement: null,
            _promiseResolver: null   // ← store the resolve function
        }
    },

    methods: {
        async open(webpageUrl, webpageId, existingElement) {
            this.webpageUrl = webpageUrl
            this.webpageId = webpageId
            this.existingElement = existingElement
            this.$refs.modalBasic.open()

            return new Promise(resolve => {
                this._promiseResolver = resolve   // keep resolver for later
            })
        },

        handleClosed() {
            if (this._promiseResolver) {
                this._promiseResolver({ success: false })   // resolved on close
                this._promiseResolver = null
            }
        },

        handleSuccess() {
            if (this._promiseResolver) {
                this._promiseResolver({ success: true })  // resolved on success
                this._promiseResolver = null
            }
            this.$refs.modalBasic.close()
        }
    }
}
</script>

<style scoped>
.element-form {
    min-width: 100%;
    width: 75vw;
    max-width: 1000px;
}
</style>