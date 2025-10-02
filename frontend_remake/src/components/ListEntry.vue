<template>
    <router-link
        :to="to"
        class="list-entry no-deco"
        @click="onClick && onClick(item)"
    >
        <i v-if="icon" :class="icon"></i>
        <div class="flex-rw space-between vertical-align">
            <div class="flex-cl">
                <label>{{ item[labelField] }}</label>
                <div v-if="subField" class="sub-field">
                    <a v-if="isLink(item[subField])" :href="item[subField]" target="_blank">
                        {{ item[subField] }}
                    </a>
                    <span v-else>{{ item[subField] }}</span>
                </div>
            </div>
            <div class="controls flex-rw">
                <i 
                    v-if="onEdit" 
                    @click.prevent="onEdit(item)" 
                    class="bx bxs-edit btn btn-text btn-icon"
                ></i>
                <i 
                    v-if="onDelete" 
                    @click.prevent="onDelete(item)" 
                    class="bx bxs-trash btn btn-text btn-icon btn-danger"
                ></i>
            </div>
        </div>
    </router-link>
</template>

<script setup>
defineProps({
    item: Object,
    to: String,
    icon: String,
    labelField: { type: String, default: "name" },
    subField: String,
    onClick: Function,
    onEdit: Function,
    onDelete: Function
})

const isLink = (value) => {
    if (!value) return false
    // simple URL check
    return value.startsWith('http://') || value.startsWith('https://')
}
</script>

<style scoped>
.list-entry {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100%;
    box-sizing: border-box;
    padding: 4px 8px;
    background-color: var(--color-neutral-200);
    border-radius: var(--btn-radius);
    cursor: pointer;
    transition: var(--t-fast) background-color;
}
.list-entry:hover {
    background-color: var(--color-neutral-300);
}
.list-entry label {
    cursor: pointer;
}
.list-entry .sub-field {
    font-size: var(--fs-1);
}
.list-entry .sub-field span {
    color: var(--text-dark-secondary);
}
.list-entry .controls {
    transition: var(--t-fast) opacity;
    opacity: 0;
}
.list-entry:hover .controls {
    opacity: 1;
}
.list-entry i {
    font-size: var(--fs-5);
    padding-inline: 4px;
}
.list-entry .controls i {
    font-size: var(--fs-4);
    padding: 6px;
}

.list-entry .btn:hover {
  background-color: var(--color-neutral-400);
}
</style>
