<template>
    <ModalBasic 
        ref="modalBasic"
        :title="existingWebpage ? 'Edit webpage' : 'Create webpage'"
        :description="existingWebpage 
            ? 'Modify an existing webpages name or URL' 
            : 'Set up a new page for data extraction'"
        :icon="existingWebpage ? 'bxs-edit' : 'bx-list-plus'"
        @closed="handleClosed"
    >
        <FormWebpage
            :webpageUrl="webpageUrl"
            :webpageId="webpageId"
            :existingWebpage="existingWebpage"
            @success="handleSuccess"
        />
    </ModalBasic>
</template>

<script>
import ModalBasic from '@/components/ModalBasic.vue'
import FormWebpage from '@/components/FormWebpage.vue'

export default {
    name: 'ModalWebpage',
    components: { ModalBasic, FormWebpage },

    data() {
        return {
            visible: false,
            existingWebpage: null,
            _promiseResolver: null   // ← store the resolve function
        }
    },

    methods: {
        async open(existingWebpage) {
            console.log("existingWebpage", existingWebpage)
            this.existingWebpage = existingWebpage
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
.webpage-form {
    min-width: 100%;
    width: 75vw;
    max-width: 1000px;
}
</style>