from pytest import mark


@mark.usefixtures('integration')
def test_root_acm_extensions_adapter_register(registry, context):
    from adhocracy_core.authorization import IRootACMExtension
    root_acm_extension = registry.getAdapter(context, IRootACMExtension)
    assert root_acm_extension['principals'] != []
    assert root_acm_extension['permissions'] != []
