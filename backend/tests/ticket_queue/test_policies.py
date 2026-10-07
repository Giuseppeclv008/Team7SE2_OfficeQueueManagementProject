from ticket_queue import AllServicesPolicy, ServiceType


def test_all_services_policy_allows_every_service_for_any_counter():
    policy = AllServicesPolicy()

    assert policy.eligible_services("1") == set(ServiceType)
    assert policy.eligible_services("unknown-counter") == set(ServiceType)
