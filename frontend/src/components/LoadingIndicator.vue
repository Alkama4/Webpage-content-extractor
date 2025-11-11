<template>
    <i class="bx bx-loader-alt loading-indicator" :class="{'hidden': hidden}"></i>
</template>

<script>
export default {
    props: { 
        hidden: { 
            type: Boolean, 
            required: true
        }
    }
}
</script>

<style scoped>
.bx-loader-alt {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to   { transform: translate(-50%, -50%) rotate(360deg); }
}

</style>
