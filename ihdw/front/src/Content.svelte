<script>
    import Loading from  './Loading.svelte'
    import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

    export let api;
    export let category;
    export let id;
    let data;
    let relations;
    let searchResults;
    let mdeData = {};

    let new_content_name = '';
    let new_content_type = 'text';
    let new_content_category_relation = '';

    async function loadData() {
        if (api) {
            data = await api.getContent(id, category);
            relations = await api.getRelations(id, category);
            searchResults = {}
            for (const key in relations) {
                if (!Object.keys(searchResults).includes(relations[key][0]))
                    searchResults[relations[key][0]] = await api.searchContent(relations[key][0], '')
            }
        }
    }

    const setMDE = el => {
        mdeData[el.id] = new window.SimpleMDE({element: el})
        mdeData[el.id].value(data[el.id].content)
        mdeData[el.id].codemirror.on("change", function(){
            clearTimeout(mdeData[el.id].timeout);
            mdeData[el.id].timeout = setTimeout(function() {   
                update_data(el.id, 'markdown', mdeData[el.id].value());
            }, 1000);
        });
    }

    async function delete_data(name){
        api.delete_data(id, category, name)
        loadData()
    }

    async function add_data(){
        api.add_data(id, category, new_content_name, new_content_type, '')
        new_content_name = '';
        new_content_type = 'text';
        loadData()
    }

    async function delete_relation(name){
        api.delete_relation(id, category, name)
        loadData()
    }

    async function add_relation(){
        api.add_relation(id, category, new_content_name, new_content_category_relation)
        new_content_name = '';
        new_content_type = 'text';
        new_content_category_relation = '';
        loadData()
    }

    async function update_data(name, type, value) {
        api.add_data(id, category, name, type, value)
    }

    async function delete_content() {
        var r = confirm("Do you really want to delete definitly this content ?");
        if (r) {
            api.delete_content(id, category);
            dispatch('close');
        }
    }

    $: loadData()
    
</script>

<svelte:head>
    
</svelte:head>

<aside class="content">
{#if data && relations && searchResults}
    {#each Object.keys(data) as key}
    <details>
        <summary>{key}</summary>
        {#if data[key].type == 'markdown'}
            <textarea id="{key}" use:setMDE></textarea>
        {/if}
        {#if data[key].type == 'text'}
            <input on:change={(e) => update_data(key, 'text', e.target.value)} bind:value={data[key].content}>
        {/if}
        {#if data[key].type == 'number'}
            <input on:change={(e) => update_data(key, 'number', e.target.value)} type='number' bind:value={data[key].content}>
        {/if}
        {#if data[key].type == 'date'}
            <input on:change={(e) => update_data(key, 'date', e.target.value)} type='date' bind:value={data[key].content}>
        {/if}
        {#if (!['name', 'date'].includes(key))}
            <a href="#" on:click="{() => delete_data(key)}">Delete</a>
        {/if}
    </details>
    {/each}
    {#each Object.keys(relations) as key}
    <details>
        <summary>{key}</summary>
        <select bind:value={relations[key][1]}>
            {#if searchResults[relations[key][0]]}
            {#each searchResults[relations[key][0]] as search}
            <option value={search.id}>
                {search.preview_name} - {search.preview_data}
            </option>
            {/each}
            {/if}
        </select>
        <a href="#" on:click="{() => delete_relation(key)}">Delete</a>
    </details>
    {/each}
    <hr>
    <input type="text" placeholder="Name" bind:value={new_content_name}>
    <select bind:value={new_content_type}>
        <option value="text">text</option>
        <option value="number">number</option>
        <option value="date">date</option>
        <option value="markdown">markdown</option>
        <option value="relation">relation</option>
    </select>
    {#if new_content_type == "relation"}
        {#await api.getCategories()}
            <Loading enabled=True/>
        {:then categories}
            <select bind:value={new_content_category_relation}>
                <option value=''>Choose a relation category</option>
                {#each categories as category}
                     <option value={category}>{category}</option>
                {/each}
            </select>
        {/await}
    {/if}
    <button on:click="{() => {if(new_content_type != 'relation') {add_data()} else {add_relation()} }}">Add</button>
    <hr>
    <a href="#" on:click={delete_content}>Delete (/!\)</a>
{:else}
<Loading enabled=true />
{/if}
</aside>

<style>
	.content {
    width: var(--width-card)+500;
}
hr {
    margin: 1rem 0;
}
button {
    padding: 0.5rem;
}
</style>