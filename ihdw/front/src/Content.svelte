<script>
    import Loading from  './Loading.svelte'
import Login from './Login.svelte';
    export let api;
    export let category;
    export let id;
    let data;
    let relations;
    let mdeData = {};

    async function loadData() {
        if (api) {
            data = await api.getContent(id, category);
            relations = await api.getRelations(id, category);
        }
    }

    const setMDE = el => {
        mdeData[el.id] = new window.SimpleMDE({element: el})
        mdeData[el.id].value(data[el.id].content)
    }

    $: loadData()
    
</script>

<svelte:head>
    
</svelte:head>

<aside class="content">
{#if data && relations}
    {#each Object.keys(data) as key}
    <details>
        <summary>{key}</summary>
        {#if data[key].type == 'markdown'}
            <textarea id="{key}" use:setMDE></textarea>
        {/if}
        {#if data[key].type == 'text'}
            <input bind:value={data[key].content}>
        {/if}
        {#if data[key].type == 'number'}
            <input type='number' bind:value={data[key].content}>
        {/if}
        {#if data[key].type == 'date'}
            <input type='date' bind:value={data[key].content}>
        {/if}
    </details>
    {/each}
    <hr>
    {#each Object.keys(relations) as key}
    <details>
        <summary>{key}</summary>
    </details>
    {/each}
{:else}
<Loading enabled=true />
{/if}
</aside>

<style>
	.content {
    width: var(--width-card)+500;
}
</style>