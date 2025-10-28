<template>
    <teleport to="body">
        <div v-if="visible" class="modal-confirmation" @click="close">
            <div class="card" @click.stop>
                <div class="header">{{ title }}</div>

                <div class="desc">{{ description }}</div>

                <div v-if="confirmationText" class="confirmation-text">
                    <input id="confirmBox" type="checkbox" v-model="confirmed">
                    <label for="confirmBox">{{ confirmationText }}</label>
                </div>

                <div class="buttons gap-8">
                    <button @click="close" class="btn-text">{{ optionNegative }}</button>
                    <button
                        @click="handleSuccess"
                        :class="{ 'btn-danger': redHover }"
                        :disabled="!confirmed && !!confirmationText"
                    >
                        {{ optionPositive }}
                    </button>
                </div>
            </div>
        </div>
    </teleport>
</template>


<script>
export default {
    name: 'ModalConfirmation',
    data() {
        return {
            visible: false,
            confirmed: false
        }
    },
    emits: ['closed'],
    props: {
        title: { type: String, default: 'Confirm' },
        description: { type: String, default: 'Are you sure?' },
        optionNegative: { type: String, default: 'Cancel' },
        optionPositive: { type: String, default: 'Yes' },
        redHover: { type: Boolean, default: false },
        confirmationText: { type: String, default: '' }
    },
    methods: {
        async open() {
            this.visible = true;

            return new Promise(resolve => {
                this._promiseResolver = resolve   // keep resolver for later
            })
        },

        close() {
            this.handleClosed();
            this.visible = false;
            this.confirmed = false
        },

        handleSuccess() {
            if (this._promiseResolver) {
                this._promiseResolver(true)  // resolved on success
                this._promiseResolver = null
            }
            this.close()
        },

        handleClosed() {
            if (this._promiseResolver) {
                this._promiseResolver(false)   // resolved on close
                this._promiseResolver = null
            }
        }
    },
}
</script>

<style scoped>
.modal-confirmation {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #00000057;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px;
    cursor: pointer;
    
    z-index: 100;
}

.card {
    cursor: auto;
    min-width: 350px;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.header {
    color: var(--text-dark-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
}

.desc {
    color: var(--text-dark-primary);
    font-size: var(--fs-2);
    line-height: 1.5;
}

.confirmation-text {
    display: flex;
    flex-direction: row;
    gap: 4px;
    font-size: var(--fs-1);
    color: var(--text-dark-secondary);
}
.confirmation-text input,
.confirmation-text label {
    cursor: pointer;
}

.buttons {
    display: flex;
    justify-content: end;
    flex-direction: row;
}

</style>