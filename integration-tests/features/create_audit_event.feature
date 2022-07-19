Feature: Create audit event
    As a Hospital Manager
    I want documentary evidence of events recorded
    So that I am audit compliant

    Background:
        Given I have a valid JWT

    Scenario: Create audit event
        When an audit event is received
        Then the audit event is stored

    Scenario: Create audit event v1
        When an audit event v1 is received
        Then the audit event v1 is stored

    Scenario: v2 -> v1 backward compatibility
        When an audit event is received
        Then the audit event is v1 compatible
