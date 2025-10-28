<template>
    <ModalBasic 
        ref="modalBasic"
        title="Edit webpage schedule"
        description="Adjust the schedule for an existing webpage."
        icon="bx-time-five"
        @closed="handleClosed"
    >
        <FormSchedule
            :existingWebpage="existingWebpage"
            @success="handleSuccess"
        />
    </ModalBasic>
</template>

<script>
import ModalBasic from '@/components/ModalBasic.vue'
import FormSchedule from '@/components/FormSchedule.vue'

export default {
    name: 'ModalSchedule',
    components: { ModalBasic, FormSchedule },

    data() {
        return {
            existingWebpage: null,
            _promiseResolver: null   // store the resolve function
        }
    },

    methods: {
        async open(existingWebpage) {
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
.form-schedule {
    min-width: 100%;
    width: 50vw;
    max-width: 1000px;
}
</style>