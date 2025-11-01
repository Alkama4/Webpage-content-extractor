<template>
    <teleport to="body">
        <div 
            v-if="visible"
            class="modal-basic"
            @click="close"
        >
            <CardBasic
                :title="title"
                :description="description"
                :icon="icon"
                @click.stop
            >
                <slot></slot>
            </CardBasic>
        </div>
    </teleport>
</template>

<script>
import CardBasic from './CardBasic.vue';

export default {
    name: 'ModalBasic',
    components: {
        CardBasic
    },
    data() {
        return {
            visible: false,
        }
    },
    emits: ['closed'],
    props: {
        title: { type: String, default: 'Untitled' },
        description: { type: String, default: 'Untitled' },
        icon: { type: String, default: 'bxs-grid' }
    },
    methods: {
        open() {
            this.visible = true;
        },
        close() {
            this.$emit('closed');
            this.visible = false;
        }
    },
    unmounted() {

    }
}
</script>

<style scoped>
.modal-basic {
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
    
    z-index: var(--z-modal);
}

.card {
    cursor: auto;
}

</style>